# -*- coding: utf-8 -*-

from django.contrib import admin

from sms.models import SmsModel

################################################################################################################
################################################################################################################

#СМСки
class SmsModelAdmin(admin.ModelAdmin):
	list_display = ('to', 'text', 'get_icon_status', 'date')
	search_fields = ('to',)
	list_filter = ('date',)
	
	def has_add_permission(self, request):
		return False
		
	def has_delete_permission(self, request, obj=None):
		return False

admin.site.register(SmsModel, SmsModelAdmin)

################################################################################################################
################################################################################################################
