# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from pay.models import Pay

#######################################################################################################################
#######################################################################################################################

class PayAdmin(admin.ModelAdmin):
	list_display = ('orderid', 'txnid', 'amount', 'currency', 'txnfee', 'paymenttype', 'merchantnumber', 'date', 'is_paid', 'get_link', 'get_order')
	search_fields = ('txnid', 'orderid')
	list_filter = ('is_paid', 'merchantnumber', 'paymenttype', 'currency')
	date_hierarchy = 'date'
	fieldsets = (
		(None, {'fields': 
			('orderid', 'txnid', 'amount', 'currency', 'txnfee', 'paymenttype', 'merchantnumber', 'date', 'is_paid', 'get_link', 'get_order')
		}),
	)
	readonly_fields = ('txnid', 'orderid', 'amount', 'currency', 'txnfee', 'paymenttype', 'merchantnumber', 'date', 'get_link', 'get_order')
	
	def has_add_permission(self, request):
		return False
		
	def has_delete_permission(self, request, obj=None):
		return False

admin.site.register(Pay, PayAdmin)

#######################################################################################################################
#######################################################################################################################