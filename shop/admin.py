# -*- coding: utf-8 -*-

from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from sorl.thumbnail.admin import AdminImageMixin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.filterspecs import FilterSpec
from django.contrib.admin.SimpleListFilter import *
from django.contrib import messages
import pickle

from mptt.admin import MPTTModelAdmin, MPTTChangeList
from django.contrib.admin.views.main import ChangeList

from shop.models import Category, Printer, Product, Order, OrderProduct, OrderStatus
from shop.filter import SortTitleFilterSpec
from shop.actions import ChangeCategoryAction, SendMessageAction

################################################################################################################
################################################################################################################

class ChangeListSaveFilter(ChangeList):
	def __init__(self, request, model, *args, **kwargs):
		self.params = dict(request.GET.items())
		session_key = 'change_list_get_query_%s' % model._meta.object_name
		
		if not self.params and session_key in request.session:
			p = pickle.loads(request.session[session_key])
			self.params, request.GET = p[0], p[1]
		
		request.session[session_key] = pickle.dumps([self.params, request.GET])
		super(ChangeListSaveFilter, self).__init__(request, model, *args, **kwargs)
		self.params['all'] = True
	
class ModelAdminSaveFilter(admin.ModelAdmin):
	def get_changelist(self, request, **kwargs):
		return ChangeListSaveFilter
		
################################################################################################################
################################################################################################################

class MPTTChangeListSaveFilter(MPTTChangeList, ChangeListSaveFilter):
    pass
	
class MPTTAdminSaveFilter(MPTTModelAdmin):
	def get_changelist(self, request, **kwargs):
		return MPTTChangeListSaveFilter

#Категории
class CategoryAdmin(AdminImageMixin, MPTTAdminSaveFilter):
	list_display = ('id', 'title', 'cod', 'is_active', 'sort')
	search_fields = ('title',)
	list_filter = ('is_active',)
	fieldsets = ((None, {'fields': ('title', 'cod', 'is_active', 'sort')}),)
	list_display_links = ('id', 'title')

admin.site.register(Category, CategoryAdmin)

################################################################################################################
################################################################################################################

#Модель принтера
class PrinterAdmin(ModelAdminSaveFilter):
	list_display = ('id', 'title', 'is_active', 'sort')
	list_display_links = ('id', 'title')
	search_fields = ('title',)
	list_filter = ('is_active',)
	ordering = ('title', '-id')

admin.site.register(Printer, PrinterAdmin)

################################################################################################################
################################################################################################################
	
#Товар
class ProductAdmin(ModelAdminSaveFilter):
	actions = [ChangeCategoryAction]
	list_display = ('id', 'title', 'code', 'category', 'printer', 'cost', 'is_checked', 'is_active', 'sort')
	list_display_links = ('id', 'title')
	search_fields = ('title', 'code')
	list_filter = ('is_checked', 'is_active', 'category', 'printer')
	fieldsets = (
		(None, {'fields': 
				('category', 'printer', 'title', 'code', 'cost', 'resource', 'is_checked', 'is_active', 'sort')
			}
		),
	)
	ordering = ('sort', '-id',)

FilterSpec.filter_specs.insert(0, (lambda f: f.name == 'category', SortTitleFilterSpec))
	
admin.site.register(Product, ProductAdmin)

################################################################################################################
################################################################################################################
		
#Корзина пользователя
class OrderProductInline(admin.TabularInline):
	template = 'shop/admin/shop_order_tabular.html'
	model = OrderProduct
	fields = ('ids', 'title', 'product', 'count_user', 'count_cancel', 'count', 'cost', 'total')
	readonly_fields = ['ids', 'title', 'count', 'total']
	can_delete = False
	extra = 0

	def ids(self, obj):
		return u'<strong>#%d</strong>' % obj.product.id
	ids.short_description = _("Id")
	ids.allow_tags = True
	
	def title(self, obj):
		return u'<strong>%s %s %s</strong>' % (obj.product.category.title, obj.product.printer.title, obj.product.title)
	title.short_description = _("Product")
	title.allow_tags = True
	
	def total(self, obj):
		return _('<strong>%d rub.</strong>') % obj.get_total_cost()
	total.short_description = _("Total")
	total.allow_tags = True

#Заказы
class OrderAdmin(AdminImageMixin, ModelAdminSaveFilter):
	change_form_template = 'shop/admin/shop_order_change_form.html'
	
	inlines = [OrderProductInline]
	actions = [SendMessageAction]
	list_display = ('id', 'name', 'is_new', 'is_paid', 'email', 'phone', 'mbphone', 'is_org', 'status', 'date')
	list_display_links = ('id', 'name')
	search_fields = ('name', 'email', 'phone', 'mbphone')
	list_filter = ('date', 'is_new', 'is_paid', 'is_org', 'status')
	readonly_fields = ('get_total_cost_tag',)
	fieldsets = (
		(None, {'fields': ('name', 'email', 'phone', 'mbphone', 'address', 'is_org', 'inn', 'status', 'text', 'is_new', 'is_paid', 'get_total_cost_tag')}),
		(_('Delivery'), {'fields': ('is_delivery', 'cost_delivery')}),
	)
	ordering = ('-date',)
	
	def queryset(self, request):
		return super(OrderAdmin, self).queryset(request).filter(is_history=True)
		
	def save_model(self, request, obj, form, change):
		obj.is_new = False
		obj.save()
		
	def get_urls(self):
		urls = super(OrderAdmin, self).get_urls()
		admin_site = self.admin_site
		opts = self.model._meta
		info = opts.app_label, opts.module_name,
		tmp_urls = patterns("",
			url("^cancel/([0-9]+)/$", admin_site.admin_view(self.cancel_view), name='%s_%s_ordercancel' % info),
		)
		return tmp_urls + urls
		
	def cancel_view(self, request, object_id, extra_context=None):
		model = self.model
		opts = model._meta
		obj = get_object_or_404(self.model, pk=object_id)
		
		for i in obj.get_op():
			i.count_cancel = i.count_user
			i.save()
		obj.save()
		
		if not obj.get_total_count():
			obj.status = OrderStatus.objects.get(is_cancel=True)
			obj.save()
			
		messages.add_message(request, messages.INFO, _("Order cleaned"))
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	
FilterSpec.filter_specs.insert(0, (lambda f: f.name == 'status', SortTitleFilterSpec))

admin.site.register(Order, OrderAdmin)

################################################################################################################
################################################################################################################

#Статус заказа
class OrderStatusAdmin(ModelAdminSaveFilter):
	list_display = ('id', 'title', 'is_new', 'is_last', 'is_cancel', 'is_georgia_received', 'is_pending_payment', 'is_cargo_shipped', 'is_active', 'sort')
	list_display_links = ('id', 'title')
	search_fields = ('title',)
	list_filter = ('is_active',)
	ordering = ('title','-id')
	
	def has_add_permission(self, request):
		return False
		
	def has_delete_permission(self, request, obj=None):
		return False

admin.site.register(OrderStatus, OrderStatusAdmin)

################################################################################################################
################################################################################################################
