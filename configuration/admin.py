# -*- coding: utf-8 -*-

from django.contrib import admin

################################################################################################################
################################################################################################################

from configuration.models import ConfigModel

class ConfigAdmin(admin.ModelAdmin):
	list_display = ('organization', 'phone1', 'operating_time')
	
	def has_add_permission(self, request):
		return False
		
	def has_delete_permission(self, request, obj=None):
		return False

#admin.site.register(ConfigModel, ConfigAdmin)

################################################################################################################
################################################################################################################
