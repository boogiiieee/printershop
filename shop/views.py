# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext, loader, RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.views.generic import list_detail
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.db.models import Avg, Max, Min, Count, Sum
from django.contrib.sitemaps import Sitemap
import datetime
import re
import os

from fpdf import FPDF

from configuration.models import ConfigModel
from pay.views import pre_pay, get_pay

from shop.helper import letter_send_mail

from shop.models import Category, Product, Order, OrderProduct, HashOrderBuy
from shop.forms import SearchMinForm, SearchForm, BasketForm, OrderForm

################################################################################################################
################################################################################################################

#Для карты сайта
class CategorySitemap(Sitemap):
	changefreq = "monthly"
	priority = 0.5
	
	def items(self):
		return Category.objects.filter(is_active=True)
		
	def location(self, obj):
		return obj.get_absolute_url()
		
################################################################################################################
################################################################################################################

from admin_tools.dashboard.modules import DashboardModule

class OrdersModule(DashboardModule):
	def is_empty(self):
		return self.objects == None

	def __init__(self, **kwargs):
		super(OrdersModule, self).__init__(**kwargs)
		self.title = _('New orders')
		self.template = 'shop/blocks/orders.html'
		self.objects = Order.objects.filter(is_new=True, is_history=True)[:10]
		
################################################################################################################
################################################################################################################

#Фильтры и сортировки товара
def product_filter(request, product_list):
	#Расширенный поиск по категории
	if 'c' in request.GET and request.GET.get('c') != '':
		try: c = int(request.GET.get('c'))
		except ValueError: pass
		else:
			try: categorys_idx = [x.id for x in Category.objects.get(id=c, is_active=True).get_descendants(include_self=True).filter(is_active=True)]
			except: pass
			else: product_list = product_list.filter(category__id__in=categorys_idx)
		
	#Фильтр по модели принтера
	if 'p' in request.GET and request.GET.get('p') != '':
		try: p = int(request.GET.get('p'))
		except: pass
		else:
			product_list = product_list.filter(printer__id=p)
		
	#Сортировка
	if 'o' in request.GET and request.GET.get('o') != '':
		o = request.GET.get('o')
		if o == '0': product_list = product_list.order_by('min_cost')
		elif o == '1': product_list = product_list.order_by('title')
		elif o == '2': product_list = product_list.order_by('-date','-id')
		
	return product_list

################################################################################################################
################################################################################################################

#Возвращает список категорий
def shop_category(request, template, extra_context=None, context_processors=None, template_loader=loader):
	c = RequestContext(request, {
		'category_list':Category.objects.filter(is_active=True)
	}, context_processors)
	
	if extra_context:
		for key, value in extra_context.items():
			if callable(value): c[key] = value()
			else: c[key] = value
	t = template_loader.get_template(template)
	
	return HttpResponse(t.render(c))
	
################################################################################################################
################################################################################################################

#Возвращает список товаров
def shop_product(request, id, template, extra_context=None, context_processors=None, template_loader=loader):
	try: ct = Category.objects.get(id=id, is_active=True)
	except: raise Http404()
	
	product_list = Product.objects.filter(category=ct, is_active=True).distinct().order_by('printer', 'title', 'cost')
	
	#Фильтры и сортировки
	product_list = product_filter(request, product_list)
		
	c = RequestContext(request, {'id':id, 'ct':ct, 'product_list':product_list}, context_processors)
	
	if extra_context:
		for key, value in extra_context.items():
			if callable(value): c[key] = value()
			else: c[key] = value
			
	t = template_loader.get_template(template)
	return HttpResponse(t.render(c))

################################################################################################################
################################################################################################################

#Мин. корзина
@never_cache 
def shop_basket_ajax(request, template):
	if request.is_ajax():
		b, create = Order.objects.get_or_create(session=request.shop_session, is_history=False)
		return render_to_response(template, {'count':b.get_total_count()})
	return HttpResponse('')

################################################################################################################
################################################################################################################

#Добавить товар в корзину
@never_cache 
def basket_add(request):
	if request.is_ajax():
		if request.method == 'GET' and request.shop_session:
			if 'id' in request.GET:
				try: id = int(request.GET.get('id'))
				except: pass
				else:
					o, create = Order.objects.get_or_create(session=request.shop_session, is_history=False)
					try: p = Product.objects.get(is_active=True, id=id)
					except: return HttpResponse('-1')
					else:
						op, create = OrderProduct.objects.get_or_create(order=o, product=p)
						op.count_user += 1
						op.save()
						return HttpResponse('1')
		return HttpResponse('-1')
	return Http404()
	
#Очистить корзину
def basket_clean(request):
	try: o = Order.objects.get(session=request.shop_session, is_history=False)
	except: messages.add_message(request, messages.INFO, _("Error basket cleaned"))
	else:
		o.delete()
		messages.add_message(request, messages.INFO, _("Basket cleaned"))
	return HttpResponseRedirect('/basket/')
	
################################################################################################################
################################################################################################################

@never_cache 
def ajax_basket_min(request):
	b, create = Order.objects.get_or_create(session=request.shop_session, is_history=False)
	return render_to_response('shop/basket/basket-min.html', {'count':b.get_total_count()}, RequestContext(request))
	
################################################################################################################
################################################################################################################

#Корзина
@never_cache 
def shop_basket(request, template, extra_context=None, context_processors=None, template_loader=loader):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except TypeError: raise Http404()
	
	BasketFormSet = modelformset_factory(OrderProduct, form=BasketForm, fields=('product', 'count_user'), extra=0, can_delete=True)
	o, create = Order.objects.get_or_create(session=request.shop_session, is_history=False)
	op = o.get_op()
	
	history_list = Order.objects.filter(session=request.shop_session, is_history=True).order_by('-date')
	if request.method == 'POST':
		formset = BasketFormSet(request.POST, queryset=op)
		if formset.is_valid():
			formset.save()
			messages.add_message(request, messages.INFO, _("Basket saved"))
			return HttpResponseRedirect('/basket/')
	else:
		formset = BasketFormSet(queryset=op)
	
	c = {'o':o, 'formset':formset}
	
	if extra_context:
		for key, value in extra_context.items():
			if callable(value): c[key] = value()
			else: c[key] = value
	
	return list_detail.object_list(
		request,
		queryset = history_list,
		paginate_by = settings.PAGINATE_BY,
		page = page,
		template_name = template,
		template_object_name = 'history',
		context_processors = context_processors,
		template_loader = template_loader,
		extra_context = c,
	)

################################################################################################################
################################################################################################################

#Сделать заказ
@never_cache 
def shop_order(request, template, extra_context=None, context_processors=None, template_loader=loader):
	o, create = Order.objects.get_or_create(session=request.shop_session, is_history=False)
	
	if request.method == 'POST':
		form = OrderForm(request.POST, instance=o)
		if form.is_valid():
			form.save()

			if o.is_delivery_pay():
				o.is_delivery = True
				o.cost_delivery = o.is_delivery_pay()
				
			o.is_history = True
			o.save()
			
			if o.email:
				domain = Site.objects.get_current().domain
				letter_send_mail(
					'mail/order_accepted.html', 
					_('Order is accepted. Order %(id)d in %(domain)s.') % {'id':o.id, 'domain':domain},
					[o.email,], 
					{'obj':o, 'domain':domain,},
				)
			
			return HttpResponseRedirect('/basket/order/thanks/')
	else: form = OrderForm()
		
	c = RequestContext(request, {'o':o, 'form':form}, context_processors)
	
	if extra_context:
		for key, value in extra_context.items():
			if callable(value): c[key] = value()
			else: c[key] = value
	t = template_loader.get_template(template)
	
	return HttpResponse(t.render(c))
	
################################################################################################################
################################################################################################################

#Спасибо за заказ + инфо
@never_cache 
def shop_order_thanks(request, template, extra_context=None, context_processors=None, template_loader=loader):
	try:
		o = Order.objects.filter(session=request.shop_session, is_history=True).latest('id')
	except: raise Http404()
	
	c = {'o':o}
	
	if extra_context:
		for key, value in extra_context.items():
			if callable(value): c[key] = value()
			else: c[key] = value
			
	return render_to_response('shop/basket/order_thanks.html', c, RequestContext(request))
	
################################################################################################################
################################################################################################################

#Оплатить заказ
@never_cache 
def shop_order_buy(request, template, extra_context=None, context_processors=None, template_loader=loader):
	if 'id' in request.GET:
		id = request.GET.get('id')
		
		try: hash = HashOrderBuy.objects.get(hash=id)
		except: pass
		else:
			o = hash.order
			
			c = {'id':id, 'o':o}
	
			if extra_context:
				for key, value in extra_context.items():
					if callable(value): c[key] = value()
					else: c[key] = value
			
			return render_to_response(template, c, RequestContext(request))
	raise Http404()
	
#Спасибо за оплату
@never_cache 
def shop_order_buy_thanks(request, template, extra_context=None, context_processors=None, template_loader=loader):
	id, o = None, None
	
	if 'orderid' in request.GET:
		id = get_pay(request.GET.get('orderid'))
	
	if id:
		o = id.shop_order
		
	c = {'id':id, 'o':o}
	
	if extra_context:
		for key, value in extra_context.items():
			if callable(value): c[key] = value()
			else: c[key] = value
			
	return render_to_response(template, c, RequestContext(request))
	
################################################################################################################
################################################################################################################

# ALTER TABLE shop_product ADD COLUMN tsv tsvector;
# UPDATE shop_product SET tsv = to_tsvector('russian', coalesce(title,'') || ' ' || coalesce(description,''));
# CREATE INDEX shop_product_tsv_idx ON shop_product USING gin(tsv);
# CREATE TRIGGER tsvectorupdate_product BEFORE INSERT OR UPDATE ON shop_product FOR EACH ROW EXECUTE PROCEDURE tsvector_update_trigger(tsv, 'pg_catalog.russian', title, description);
# ALTER TABLE shop_category ADD COLUMN tsv tsvector;
# UPDATE shop_category SET tsv = to_tsvector('russian', coalesce(title,''));
# CREATE INDEX shop_category_tsv_idx ON shop_category USING gin(tsv);
# CREATE TRIGGER tsvectorupdate_category BEFORE INSERT OR UPDATE ON shop_category FOR EACH ROW EXECUTE PROCEDURE tsvector_update_trigger(tsv, 'pg_catalog.russian', title);

#Поиск по товарам
def shop_simple_search(request, template, extra_context=None, context_processors=None, template_loader=loader):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except TypeError: raise Http404()
	
	text = u''
	if 'q' in request.GET and len(request.GET.get('q')) > 2:
		text = u'%s' % request.GET.get('q')

		
		
		product_list = Product.objects.filter(is_active=True)
		for key in re.findall(ur'([а-яА-яa-zA-Z0-9]+)', text):
			product_list = product_list.filter(
				Q(category__title__icontains=key) | Q(printer__title__icontains=key) | Q(title__icontains=key) | Q(code__icontains=key)
			)
		
		
		
		# keywords = unicode(":*|".join(re.findall(ur'([а-яА-яa-zA-Z0-9]+)', text))) + u":*"
		# full = Product.objects.filter(is_active=True).extra(
			# select={
				# 'rank': '''
					# ts_rank(
						# array[0.1,0.3,0.5,0.9],
						# setweight(shop_product.tsv, 'A') ||
						# setweight(shop_category.tsv, 'B'),
						# to_tsquery(%s)
					# )
				# ''',
			# },
			# tables = ['shop_product', 'shop_category'],
			# where = [
				# '''
					# shop_product.tsv @@ to_tsquery(%s) OR 
					# shop_category.tsv @@ to_tsquery(%s)
				# ''',
				# 'shop_product.category_id = shop_category.id',
			# ],
			# params = [keywords]*2,
			# select_params = [keywords],
		# ).distinct().order_by('-rank')[:300]
		
		# ids, case_id, loop = [], 'CASE', 1
		# for x in full:
			# ids.append(x.id)
			# case_id += " WHEN \"shop_product\".\"id\"='%d' THEN %d" % (x.id, loop)
			# loop += 1
		# case_id += " ELSE %d END, \"shop_product\".\"id\"" % (len(full)+1,)
		
		# product_list = Product.objects.select_related().filter(id__in=ids, is_active=True).extra(select={'case_id':case_id}, order_by=['case_id']).distinct()
	else: product_list = Product.objects.filter(is_active=True)
		
	#Фильтры и сортировки
	product_list = product_filter(request, product_list)
	
	c = {'shop_search_text':u'%s'%text, 'shop_search_count':product_list.count()}
	if extra_context:
		for key, value in extra_context.items():
			if callable(value): c[key] = value()
			else: c[key] = value
			
	return list_detail.object_list(
		request,
		queryset = product_list,
		paginate_by = settings.PAGINATE_BY,
		page = page,
		template_name = template,
		template_object_name = 'product',
		context_processors = context_processors,
		template_loader = template_loader,
		extra_context = c,
	)

################################################################################################################
################################################################################################################

#Отчет
def report(request):
	dt = datetime.datetime.now()
	
	from django import forms
	from django.forms.extras import SelectDateWidget
	class AdminReportForm(forms.Form):
		stdate = forms.DateField(label=_('Satrt date'), widget=SelectDateWidget(years=range(dt.year-5, dt.year+1)))
		spdate = forms.DateField(label=_('Stop date'), widget=SelectDateWidget(years=range(dt.year-5, dt.year+1)))
	
	stdate, spdate = dt-datetime.timedelta(days=30), dt
	
	if request.method == 'POST':
		form = AdminReportForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			stdate, spdate = cd['stdate'], cd['spdate']
			
			o = Order.objects.filter(Q(date__gte=stdate) & Q(date__lte=spdate))
			
			unique_customers = []
			total_processed = 0
			turnover = 0
			cartridges_statistic = {}
			
			#Всего заказов
			total_orders = o.filter(is_history=True).count()
			#Кол-во оплаченных заказов
			paid_orders = o.filter(is_paid=True, is_history=True).count()
			
			for i in o.filter(is_history=True):
				#Оборот за заданный период
				turnover += i.get_total_cost()
				
				#Кол-во уникалных клиентов
				if not i.session in unique_customers:
					unique_customers.append(i.session)
					
				#Общее количество обработанных картриджей
				total_processed += i.get_total_count()
				
				for j in i.get_op():
					key = str(j.product.id)
					if not key in cartridges_statistic:
						cartridges_statistic[key] = {
							'product': j.product, 
							'processed_cartridges': 0, #Количество обработанных картриджей по каждому типу за заданный период
							'abandoned_cartridges': 0, #Количество и типы отказных картриджей (в переработке которых было отказано клиенту)
						}
					cartridges_statistic[key]['processed_cartridges'] += j.count
					cartridges_statistic[key]['abandoned_cartridges'] += j.count_cancel

			statistic = []
			for key, value in sorted(cartridges_statistic.items(), key = lambda x: -x[1]['processed_cartridges']):
				statistic.append(value)

			unique_customers = len(unique_customers)
			data = True
	else:
		form = AdminReportForm(initial={'stdate':stdate, 'spdate':spdate})
		
	return render_to_response('shop/admin/report.html', locals(), RequestContext(request))
	
################################################################################################################
################################################################################################################

#Сохранить историю
@login_required
def save_history(request):
	stdate, spdate = None, None
	
	if 'stdate' in request.GET:
		stdate = datetime.datetime.strptime(request.GET.get('stdate'), '%d.%m.%Y')
	if 'spdate' in request.GET:
		spdate = datetime.datetime.strptime(request.GET.get('spdate'), '%d.%m.%Y')
		
	if stdate and spdate:
		o = Order.objects.filter(Q(date__gte=stdate) & Q(date__lte=spdate)).order_by('date')
		domain = Site.objects.get_current().domain
		
		def ImprovedTable(pdf, oo, data):
			header = [_(u"#id"), _(u"Title"), _(u"Price"), _(u"Count"), _(u"Cost")]
			w = [20, 70, 20, 20, 20]
			
			for i in range(len(header)):
				pdf.cell(w[i], 5, u'%s' % header[i], 1, 0, 'C', 1)
			pdf.ln()
			
			for row in data:
				pdf.cell(w[0], 5, u'%d' % row.product.id, 'LR')
				pdf.cell(w[1], 5, u'%s' % row.product.title, 'LR')
				pdf.cell(w[2], 5, u'%d' % row.get_cost(), 'LR', 0, 'R')
				pdf.cell(w[3], 5, u'%d' % row.count, 'LR', 0, 'R')
				pdf.cell(w[4], 5, u'%d' % row.get_total_cost(), 'LR', 0, 'R')
				pdf.ln()
				
			if oo.is_delivery:
				pdf.cell(w[0], 5, u'-', 'LR')
				pdf.cell(w[1], 5, _(u"Delivery"), 'LR')
				pdf.cell(w[2], 5, u'%d' % oo.cost_delivery, 'LR', 0, 'R')
				pdf.cell(w[3], 5, u'-', 'LR', 0, 'R')
				pdf.cell(w[4], 5, u'%d' % oo.cost_delivery, 'LR', 0, 'R')
				pdf.ln()

			pdf.cell(sum(w), 0, '', 'T')
			return pdf

		pdf = FPDF('P','mm','A4')
		pdf.set_author(domain)
		pdf.add_page()
		pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
		pdf.add_font('DejaVuBold', '', 'DejaVuSansCondensed-Bold.ttf', uni=True)
		pdf.set_fill_color(229, 229, 229);
		
		pdf.set_font('DejaVu', '', 5);
		pdf.write(5, _(u"History created at %s") % datetime.datetime.now().strftime('%d.%m.%Y %H:%M'))
		pdf.ln(5)
		
		pdf.set_font('DejaVuBold', '', 8);
		pdf.write(5, _(u"History"))
		pdf.ln(5)
			
		for x in o:
			op = x.get_op()
			if op.count():
				pdf.set_font('DejaVuBold', '', 8);
				pdf.write(5, u'Order #%d at %s on sum %d. Status: %s. Products:' % (
					x.id, x.date.strftime('%d.%m.%Y %H:%M'), x.get_total_cost(), x.status.title
				))
				pdf.ln(5)
				pdf.set_font('DejaVu', '', 5);
				pdf = ImprovedTable(pdf, x, x.get_op())
				pdf.ln(5)
		
		s = pdf.output('History.pdf', 'S')

		response = HttpResponse(s, mimetype='application/pdf; charset=cp1251')
		response['Content-Disposition'] = 'attachment; filename=History.pdf'
		return response
	return HttpResponse('')
	
################################################################################################################
################################################################################################################

#Генерирует печатную форму
def plate(request):
	try:
		o = Order.objects.filter(session=request.shop_session, is_history=True).latest('id')
		config, create = ConfigModel.objects.get_or_create(id=1)
		domain = Site.objects.get_current().domain
	except: pass
	else:	
		if config.organization and config.office1 and o.address and o.name:
			pdf = FPDF('P','mm','A4')
			pdf.set_author(domain)
			pdf.add_page()
			pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
			pdf.add_font('DejaVuBold', '', 'DejaVuSansCondensed-Bold.ttf', uni=True)
			pdf.set_fill_color(229, 229, 229);
			
			pdf.set_font('DejaVu', '', 5);
			pdf.write(9, _(u"Created by %(date)s on %(domain)s. Order #%(id)d.") % {'date':datetime.datetime.now().strftime('%d.%m.%Y %H:%M'), 'domain':domain, 'id':o.id})
			pdf.ln(9)
				
			pdf.set_font('DejaVuBold', '', 9);
			pdf.write(9, _(u"Recipient:"))
			pdf.ln(9)
			
			pdf.set_font('DejaVu', '', 8);
			if config.office1:
				pdf.write(5, _(u"Address: %s") % config.office1)
				pdf.ln(5)
			if config.organization:
				pdf.write(5, _(u"Name: %s") % config.organization)
				pdf.ln(5)
				
			pdf.set_font('DejaVuBold', '', 9);
			pdf.write(9, _(u"Sender:"))
			pdf.ln(9)
			
			pdf.set_font('DejaVu', '', 8);
			if o.address:
				pdf.write(5, _(u"Address: %s") % o.address)
				pdf.ln(5)
			if o.name:
				pdf.write(5, _(u"Name: %s") % o.name)
				pdf.ln(9)
				
			pdf.set_font('DejaVu', '', 5);
			pdf.write(5, _(u"Cut and paste on the packaging"))
			pdf.ln(5)
				
			s = pdf.output('Plate.pdf', 'S')
			
			response = HttpResponse(s, mimetype='application/pdf; charset=cp1251')
			response['Content-Disposition'] = 'attachment; filename=plate.pdf'
			return response
	return HttpResponse('')
	
################################################################################################################
################################################################################################################

#Генерирует счет-фактуру
def invoice(request):
	if 'id' in request.GET:
		id = request.GET.get('id')
		
		o = None
		try:
			o = HashOrderBuy.objects.get(order__id=id, order__session=request.shop_session).order
		except:
			try:
				o = Order.objects.get(session=request.shop_session, id=id)
			except: pass
		
		if o:
			config, create = ConfigModel.objects.get_or_create(id=1)
			domain = Site.objects.get_current().domain
			
			class PDF(FPDF):
				def footer(this):
					this.set_y(-15)
					this.set_font('DejaVu', '', 6);
					this.cell(200, 10, _(u"The origin of the sheet http://%s.") % domain, 0, 0, 'C')
			
			pdf = PDF('P','mm','A4')
			pdf.alias_nb_pages(u'~')
			pdf.set_author(domain)
			pdf.add_page()
			pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
			pdf.add_font('DejaVuBold', '', 'DejaVuSansCondensed-Bold.ttf', uni=True)
			pdf.set_fill_color(229, 229, 229);
			
			pdf.set_font('DejaVuBold', '', 25);
			pdf.write(5, _(u"Faktura"))
			
			pdf.image(os.path.join(settings.MEDIA_ROOT, 'img', 'main_text.jpg'), x=130, y=7.5, w=70, h=0)
				
			pdf.set_y(45)
			pdf.set_font('DejaVu', '', 10);
			if o.name:
				pdf.write(5, _(u"Name: %s") % o.name)
				pdf.ln(5)
			if o.phone:
				pdf.write(5, _(u"Phone: %s") % o.phone)
				pdf.ln(5)
			if o.mbphone:
				pdf.write(5, _(u"Phone: %s") % o.mbphone)
				pdf.ln(5)
			if o.email:
				pdf.write(5, _(u"E-mail: %s") % o.email)
				pdf.ln(5)
			if o.address:
				pdf.write(5, _(u"Address: %s") % o.address)
				pdf.ln(5)
			if o.inn and o.is_org:
				pdf.write(5, _(u"Inn: %s") % o.inn)
				pdf.ln(5)
			
			pdf.set_font('DejaVu', '', 8);
			pdf.set_text_color(100, 100, 100);
			if config.requisites_org:
				pdf.set_xy(100, 30)
				pdf.multi_cell(100, 5, u'%s' % config.requisites_org, 0, 'R', 0)
			if config.requisites_adr:
				pdf.set_x(100)
				pdf.multi_cell(100, 5, u'%s' % config.requisites_adr, 0, 'R', 0)
			if config.requisites_phone:
				pdf.set_x(100)
				pdf.multi_cell(100, 5, _(u"Phone: %s") % config.requisites_phone, 0, 'R', 0)
			if settings.DEFAULT_FROM_EMAIL:
				pdf.set_x(100)
				pdf.multi_cell(100, 5, settings.DEFAULT_FROM_EMAIL, 0, 'R', 0)
			if config.requisites_inn:
				pdf.set_x(100)
				pdf.multi_cell(100, 5, _(u"Inn: %s") % config.requisites_inn, 0, 'R', 0)
				
			pdf.set_font('DejaVu', '', 8);
			pdf.set_text_color(0, 0, 0);
			
			pdf.set_x(100)
			pdf.cell(40, 10, _(u"Factura:"), 0, 0, 'R', 0)
			pdf.cell(60, 10, u'%d' % o.id, 0, 1, 'R', 0)
			pdf.set_x(100)
			pdf.cell(40, 5, _(u"Kundenummer:"), 0, 0, 'R', 0)
			pdf.cell(60, 5, u'%s' % o.session, 0, 1, 'R', 0)
			pdf.set_x(100)
			pdf.cell(40, 5, _(u"Dato:"), 0, 0, 'R', 0)
			pdf.cell(60, 5, u'%s' % datetime.datetime.now().strftime('%d-%m-%Y'), 0, 1, 'R', 0)
			pdf.set_x(100)
			pdf.cell(40, 5, _(u"Side:"), 0, 0, 'R', 0)
			pdf.cell(60, 5, u'~', 0, 1, 'R', 0)
			
			pdf.set_fill_color(229, 229, 229);
			pdf.set_x(100)
			pdf.cell(40, 10, _(u"Intern faktura:"), 0, 0, 'R', 0)
			pdf.cell(60, 10, u'%d' % o.id, 0, 1, 'R', 0)
			
			#Список товаров
			header = [_(u"Factura #id"), _(u"Factura title"), _(u"Factura count"), _(u"Factura price"), _(u"Factura sale %"), _(u"Factura cost")]
			w = [20, 100, 20, 20, 10, 20]
			
			pdf.set_font('DejaVuBold', '', 6);
			for i in range(len(header)):
				pdf.cell(w[i], 5, u'%s' % header[i], 1, 0, 'C', 1)
			pdf.ln(5)
			
			pdf.set_font('DejaVu', '', 6);
			for row in o.get_op():
				pdf.cell(w[0], 5, u'%d' % row.product.id, 'LR')
				pdf.cell(w[1], 5, u'%s %s %s' % (row.product.category.title, row.product.printer.title, row.product.title), 'LR')
				pdf.cell(w[2], 5, u'%d' % row.count, 'LR', 0, 'R')
				pdf.cell(w[3], 5, u'%.2f' % float(row.get_cost()), 'LR', 0, 'R')
				pdf.cell(w[4], 5, u'-', 'LR', 0, 'R')
				pdf.cell(w[5], 5, u'%.2f' % float(row.get_total_cost()), 'LR', 0, 'R')
				pdf.ln(5)
				
			if o.is_delivery:
				pdf.cell(w[0], 5, u'', 'LR')
				pdf.cell(w[1], 5, _(u"Delivery"), 'LR')
				pdf.cell(w[2], 5, u'1', 'LR', 0, 'R')
				pdf.cell(w[3], 5, u'%.2f' % float(o.cost_delivery), 'LR', 0, 'R')
				pdf.cell(w[4], 5, u'-', 'LR', 0, 'R')
				pdf.cell(w[5], 5, u'%.2f' % float(o.cost_delivery), 'LR', 0, 'R')
				pdf.ln(5)

			pdf.cell(sum(w), 0, '', 'T')
			pdf.ln(5)
			
			#Нижняя таблица/Общая стоимость/НДС
			header = [_(u"Price without VAT"), _(u"VAT"), _(u"The amount of VAT"), _(u"In total, incl. VAT")]
			w = [40, 40, 40, 70]
			
			pdf.set_font('DejaVuBold', '', 8);
			pdf.cell(sum(w), 0, '', 'B')
			pdf.ln(0.1)
			
			pdf.cell(w[0], 5, u'%s' % header[0], 'L', 0, 'C', 0)
			pdf.cell(w[1], 5, u'%s' % header[1], 0, 0, 'C', 0)
			pdf.cell(w[2], 5, u'%s' % header[2], 0, 0, 'C', 0)
			pdf.cell(w[3], 5, u'%s' % header[3], 'R', 0, 'C', 1)
			pdf.ln()
			
			pdf.set_font('DejaVu', '', 6);
			pdf.cell(w[0], 5, u'%.2f' % (float(o.get_total_cost())-o.get_VAT(),), 'L', 0, 'C', 0)
			pdf.cell(w[1], 5, u'25%', 0, 0, 'C', 0)
			pdf.cell(w[2], 5, u'%.2f' % o.get_VAT(), 0, 0, 'C', 0)
			pdf.set_font('DejaVuBold', '', 20);
			pdf.cell(30, 5, _(u"Total factura"), 0, 0, 'L', 1)
			pdf.set_font('DejaVuBold', '', 10);
			pdf.cell(40, 5, u'%.2f' % float(o.get_total_cost()), 'R', 0, 'R', 1)
			pdf.ln()
			
			pdf.cell(sum(w), 0, '', 'T')
			
			#Сохранить Pdf
			s = pdf.output('faktura.pdf', 'S')
			
			response = HttpResponse(s, mimetype='application/pdf; charset=cp1251')
			response['Content-Disposition'] = 'attachment; filename=faktura.pdf'
			return response
	return HttpResponse('')
	
################################################################################################################
################################################################################################################