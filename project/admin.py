# -*- coding: utf-8 -*-

from django.contrib import admin

from project.models import TranslateInterface

################################################################################################################
################################################################################################################

#Перевод элементов интерфейса
class TranslateInterfaceAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'name_ru', 'title')
	search_fields = ('name', 'name_ru', 'title')
	list_editable = ('name_ru', 'title')
	exclude = ('name',)
	
	def has_add_permission(self, request):
		return False
		
	def has_delete_permission(self, request, obj=None):
		return False

admin.site.register(TranslateInterface, TranslateInterfaceAdmin)

################################################################################################################
################################################################################################################
