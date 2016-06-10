# -*- coding: utf-8 -*-

from django.db import connection, models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from tinymce import models as TinymceField
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from pytils.translit import slugify
import settings
import datetime
import uuid
import re
import os

from mptt.models import MPTTModel, TreeForeignKey

from sorl.thumbnail import ImageField as SorlImageField
from sorl.thumbnail.shortcuts import get_thumbnail, delete

from configuration.models import ConfigModel
from sms.views import Sms

from shop.helper import letter_send_mail

try: import Image
except ImportError:
	try: from PIL import Image
	except ImportError: raise ImportError("The Python Imaging Library was not found.")

################################################################################################################
################################################################################################################
		
#Категории
class Category(MPTTModel):
	parent = TreeForeignKey('self', verbose_name=_("parent"), blank=True, null=True, related_name='children_category', help_text=_('perent catefory if exist'))
	title = models.CharField(max_length=500, verbose_name=_('title'))
	slug = models.CharField(max_length=500, verbose_name=_('slug'), blank=True)
	cod = models.CharField(max_length=500, verbose_name=_('cod'), blank=True)
	text = TinymceField.HTMLField(max_length=10000, verbose_name=_('text'), blank=True, help_text=_('description category. not show'))
	image = SorlImageField(max_length=500, upload_to='upload/shop/category/', verbose_name=_('image'), blank=True, null=True)
	is_active = models.BooleanField(verbose_name=_('is active'), default=True)
	sort = models.IntegerField(verbose_name=_('sort'), default=0)
	
	def __unicode__(self):
		return self.title
			
	class Meta: 
		verbose_name = _('category') 
		verbose_name_plural = _('categorys')
		ordering = ['sort']
		
	class MPTTMeta:
		parent_attr = 'parent'
		order_insertion_by = ['sort', 'title']
		
	#Возвращает подкатегории
	def get_subcategory(self):
		return self.get_children().filter(is_active=True)
		
	def get_breadcrumbs(self):
		return list(self.get_ancestors(ascending=False, include_self=True).filter(is_active=True))
		
	@models.permalink
	def get_absolute_url(self):
		return ('subcategory_url', (), {'id':self.id, 'slug':self.slug})
		
	def small_image(self):
		if self.image:
			f = get_thumbnail(self.image, '80x60', crop='center', quality=99, format='PNG')
			html = '<a href="%s"><img src="%s" title="%s" /></a>'
			return html % (self.image.url, f.url, self.title)
		return u'<img src="/media/img/no_image_min.png" title="%s" />' % self.title

	small_image.short_description = _("Image")
	small_image.allow_tags = True
	
	def get_all_products(self):
		return self.products_category.all()
		
	def get_series(self):
		return Series.objects.filter(id__in=[x.series.id for x in ProductSeries.objects.filter(product__in=self.get_all_products())]).order_by('title').distinct()
		
	def clean(self):
		r = re.compile('^([a-zA-Z0-9_-]+)\.(jpg|jpeg|png|bmp|gif)$', re.IGNORECASE)
		if self.image:
			if not r.findall(os.path.split(self.image.url)[1]):
				raise ValidationError(_("File name validation error."))
				
		#Проверка на существование у родителя товара.
		if self.parent and Product.objects.filter(category=self.parent).count():
			raise ValidationError(_("This category have products."))

	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(Category, self).save(*args, **kwargs)
		
################################################################################################################
################################################################################################################
		
#Модель принтера
class Printer(models.Model):
	title = models.CharField(max_length=500, verbose_name=_('title'))
	is_active = models.BooleanField(verbose_name=_('is active'), default=True)
	sort = models.IntegerField(verbose_name=_('sort'), default=0)
	
	def __unicode__(self):
		return self.title
			
	class Meta: 
		verbose_name = _('printer') 
		verbose_name_plural = _('printeres')
		ordering = ['sort', 'title']
		
################################################################################################################
################################################################################################################

#Товар	
class Product(models.Model):
	category = models.ForeignKey(Category, verbose_name=_('category'), related_name='products_category')
	printer = models.ForeignKey(Printer, verbose_name=_('printer'), blank=True, null=True, related_name='product_printer')
	title = models.CharField(max_length=500, verbose_name=_('title'))
	slug = models.CharField(max_length=500, verbose_name=_('slug'), blank=True)
	code = models.CharField(max_length=500, verbose_name=_('code'), blank=True)
	resource = models.CharField(max_length=500, verbose_name=_('resource'), blank=True)
	description = TinymceField.HTMLField(max_length=10000, verbose_name=_('description'), blank=True)
	cost = models.IntegerField(verbose_name=_('cost'), default=0)

	date = models.DateField(verbose_name=_('date'), auto_now = True, auto_now_add = True)
	is_checked = models.BooleanField(verbose_name=_('is checked'), default=False)
	
	id_exelparser = models.IntegerField(blank=True, null=True)
	is_last_exelparser = models.BooleanField(default=False)
	status_exelparser = models.IntegerField(blank=True, null=True)
	date_exelparser = models.DateTimeField(blank=True, null=True)
	exelparser_title = models.CharField(max_length=500, blank=True)
	exelparser = models.CharField(max_length=500, verbose_name=_('exel parser'), blank=True)
	
	is_active = models.BooleanField(verbose_name=_('is active'), default=True)
	sort = models.IntegerField(verbose_name=_('sort'), default=0)
	
	def __unicode__(self):
		return self.title
		
	class Meta: 
		verbose_name = _('product') 
		verbose_name_plural = _('products')
		ordering = ['sort', 'title']
		
	@models.permalink
	def get_absolute_url(self):
		return ('product_url', (), {'id':self.id, 'slug': self.slug},)
		
	def get_breadcrumbs(self):
		return list(self.category.get_breadcrumbs()) + [self]
	
	def get_cost(self):
		if self.cost: return self.cost
		return 0
		
	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(Product, self).save(*args, **kwargs)
	
################################################################################################################
################################################################################################################

#Заказы
class Order(models.Model):
	session = models.CharField(max_length=200, verbose_name=_('session'))
	name = models.CharField(max_length=100, verbose_name=_('name'), blank=True)
	phone = models.CharField(max_length=100, verbose_name=_('phone'), blank=True)
	mbphone = models.CharField(max_length=100, verbose_name=_('mb phone'), blank=True)
	email = models.EmailField(max_length=100, verbose_name=_('e-mail'), blank=True)
	address = models.CharField(max_length=500, verbose_name=_('address'), blank=True)
	
	is_org = models.BooleanField(verbose_name=_('is organization'), default=False)
	inn = models.CharField(max_length=100, verbose_name=_('inn'), blank=True)
	
	text = TinymceField.HTMLField(max_length=10000, verbose_name=_('text'), blank=True)
	status = models.ForeignKey('OrderStatus', verbose_name=_('order status'), blank=True, null=True)
	products = models.ManyToManyField(Product, verbose_name=_("basket's products"), related_name='rel_products', through='OrderProduct')
	date = models.DateTimeField(verbose_name=_('date'), auto_now = True, auto_now_add = True)
	is_new = models.BooleanField(verbose_name=_('is new'), default=True)
	
	is_delivery = models.BooleanField(verbose_name=_('is delivery'), default=False)
	cost_delivery = models.IntegerField(verbose_name=_('cost delivery'), blank=True, null=True)
	
	is_history = models.BooleanField(verbose_name=_('is history'), default=False)
	is_paid = models.BooleanField(verbose_name=_('is paid'), default=False)
	
	def __unicode__(self):
		return u'#%d - %s (%s)' % (self.id, self.name, self.date.strftime("%d.%m.%Y %H:%M"))
	
	def get_op(self):
		return OrderProduct.objects.filter(order=self)
		
	def get_total_count(self):
		o = self.get_op()
		count = 0
		for i in o:
			try:
				c = int(i.count)
				if c > 0 and c < 1000000:
					count += c
			except: return 0
		return count
		
	def is_delivery_pay(self):
		config, create = ConfigModel.objects.get_or_create(id=1)
		if self.get_total_count() <= config.free_delivery:
			return config.cost_delivery
		return False
		
	def get_total_cost(self):
		o = self.get_op()
		total = 0
		for i in o:
			total += i.get_total_cost()

		if self.is_delivery and total:
			if not self.cost_delivery:
				config, create = ConfigModel.objects.get_or_create(id=1)
				self.cost_delivery = config.cost_delivery
			total += self.cost_delivery
			
		return total
		
	def get_VAT(self):
		return (float(self.get_total_cost()) * settings.SHOP_VAT)/(1 + settings.SHOP_VAT)
		
	def get_total_cost_tag(self):
		return _('<strong>%d rub.</strong>') % self.get_total_cost()
	get_total_cost_tag.short_description = _("Total cost")
	get_total_cost_tag.allow_tags = True
	
	def get_absolute_url(self):
		return '/admin/shop/order/%d/' % self.id
		
	def save(self, *args, **kwargs):
		if not self.id:
			self.status = OrderStatus.objects.get(is_active=True, is_new=True)
		else:
			if self.id and self.status and self.status != Order.objects.get(id=self.id).status:
				domain = Site.objects.get_current().domain
				
				#Груз получен
				if self.status == OrderStatus.objects.get(is_active=True, is_georgia_received=True):
					letter_send_mail(
						'mail/georgia_received.html', 
						_('Cargo received. Order %(id)d in %(domain)s.') % {'id':self.id, 'domain':domain},
						[self.email,], 
						{'obj':self, 'domain':domain,},
					)
					if self.mbphone:
						Sms(_('Cargo received. Order #%d.') % self.id, [self.mbphone,]).send()
						
				#Картриджи обработаны и ожидают оплаты
				if self.status == OrderStatus.objects.get(is_active=True, is_pending_payment=True):
					if not self.is_org:
						hob, create = HashOrderBuy.objects.get_or_create(order=self)
						if create:
							hob.hash = str(uuid.uuid4())
							hob.save()
					else: hob = None
					
					config, create = ConfigModel.objects.get_or_create(id=1)
					
					letter_send_mail(
						'mail/pending_payment.html', 
						_('Cartridges are processed and pending payment. Order %(id)d in %(domain)s.') % {'id':self.id, 'domain':domain},
						[self.email,], 
						{'obj':self, 'domain':domain, 'hob':hob, 'config':config, 'email':settings.DEFAULT_FROM_EMAIL},
					)
					if self.mbphone:
						Sms(_('Pending payment. Order #%d.') % self.id, [self.mbphone,]).send()
						
				#Груз отправлен
				if self.status == OrderStatus.objects.get(is_active=True, is_cargo_shipped=True):
					letter_send_mail(
						'mail/cargo_shipped.html', 
						_('Cargo shipped. Order %(id)d in %(domain)s.') % {'id':self.id, 'domain':domain},
						[self.email,], 
						{'obj':self, 'domain':domain,},
					)
					if self.mbphone:
						Sms(_('Cargo shipped. Order #%d.') % self.id, [self.mbphone,]).send()
						
				#Заказ отменен
				if self.status == OrderStatus.objects.get(is_active=True, is_cancel=True):
					letter_send_mail(
						'mail/order_canceled.html', 
						_('Order has been canceled. Order %(id)d in %(domain)s.') % {'id':self.id, 'domain':domain},
						[self.email,], 
						{'obj':self, 'domain':domain,},
					)
					
				#Заказ выполнен
				if self.status == OrderStatus.objects.get(is_active=True, is_last=True):
					letter_send_mail(
						'mail/order_done.html', 
						_('Order has been done. Order %(id)d in %(domain)s.') % {'id':self.id, 'domain':domain},
						[self.email,], 
						{'obj':self, 'domain':domain,},
					)
				
		super(Order, self).save(*args, **kwargs)
		
	class Meta: 
		verbose_name = _('order') 
		verbose_name_plural = _('Orders')
		ordering = ['-is_new', 'id']
	
################################################################################################################
################################################################################################################

#Корзина пользователя	
class OrderProduct(models.Model):
	order = models.ForeignKey(Order)
	product = models.ForeignKey(Product)
	count = models.IntegerField(verbose_name=_('count'), default=0)
	count_user = models.IntegerField(verbose_name=_('count user'), default=0)
	count_cancel = models.IntegerField(verbose_name=_('count cancel'), default=0)
	cost = models.IntegerField(verbose_name=_('cost'))
	date = models.DateTimeField(verbose_name=_('date'), auto_now = True, auto_now_add = True)
	
	def __unicode__(self):
		return u'%s / %s' % (self.order, self.product)
		
	def clean(self):
		if self.count > 1000000 or self.count < 0:
			raise ValidationError(_('Error count field'))
			
	def get_cost(self):
		if self.cost: return self.cost
		return 0
		
	def get_total_cost(self):
		try:
			c = self.count
			if c > 0 and c < 1000000:
				return c * self.cost
		except: pass
		return 0
		
	class Meta:
		verbose_name = _('basket') 
		verbose_name_plural = _('baskets')
		ordering = ['product', 'id']
		
	def save(self, *args, **kwargs):
		if not self.id:
			self.cost = self.product.get_cost()
			
		if self.count_cancel > self.count_user: self.count_cancel = self.count_user
		if self.count_cancel < 0: self.count_cancel = 0
			
		self.count = self.count_user - self.count_cancel
		super(OrderProduct, self).save(*args, **kwargs)

################################################################################################################
################################################################################################################

#Статус заказа
class OrderStatus(models.Model):
	title = models.CharField(max_length=500, verbose_name=_('title'))
	is_new = models.BooleanField(verbose_name=_('is new'), default=False, help_text=_('Set this status if order is new.'))
	is_last = models.BooleanField(verbose_name=_('is last'), default=False, help_text=_('Set this status if order is done.'))
	is_cancel = models.BooleanField(verbose_name=_('is cancel'), default=False, help_text=_('Set this status if order canceled.')) #Отменен
	is_georgia_received = models.BooleanField(verbose_name=_('is georgia received'), default=False, help_text=_('Send notice if georgia received.')) #Груз получен
	is_pending_payment = models.BooleanField(verbose_name=_('is pending payment'), default=False, help_text=_('Send notice if cartridges are processed and pending payment.')) #Картриджи обработаны и ожидают оплаты
	is_cargo_shipped = models.BooleanField(verbose_name=_('is cargo shipped'), default=False, help_text=_('Send notice if cargo shipped.')) #Груз отправлен
	is_active = models.BooleanField(verbose_name=_('is active'), default=True)
	sort = models.IntegerField(verbose_name=_('sort'), default=0)
	
	def __unicode__(self):
		return self.title
			
	class Meta: 
		verbose_name = _('order status') 
		verbose_name_plural = _('order statuses')
		ordering = ['sort', 'title', 'id']
		
	def save(self, *args, **kwargs):
		if self.is_new:
			OrderStatus.objects.filter(is_new=True).update(is_new=False)
		if self.is_last:
			OrderStatus.objects.filter(is_last=True).update(is_last=False)
		if self.is_cancel:
			OrderStatus.objects.filter(is_cancel=True).update(is_cancel=False)
		if self.is_georgia_received:
			OrderStatus.objects.filter(is_georgia_received=True).update(is_georgia_received=False)
		if self.is_pending_payment:
			OrderStatus.objects.filter(is_pending_payment=True).update(is_pending_payment=False)
		if self.is_cargo_shipped:
			OrderStatus.objects.filter(is_cargo_shipped=True).update(is_cargo_shipped=False)
		super(OrderStatus, self).save(*args, **kwargs)
		
################################################################################################################
################################################################################################################

#Хеш таблица заказов подлежащих оплате
class HashOrderBuy(models.Model):
	order = models.ForeignKey(Order)
	hash = models.CharField(max_length=500)
	
	def __unicode__(self):
		return u'HashOrderBuy'
		
################################################################################################################
################################################################################################################