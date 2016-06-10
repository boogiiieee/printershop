# -*- coding: utf-8 -*-

from django.contrib import admin

from questionanswer.models import QuestionAnswerItem

################################################################################################################
################################################################################################################

class QuestionAnswerItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'phone', 'date_question', 'is_active', 'sort')
	search_fields = ('name', 'email', 'phone')
	list_filter = ('is_active',)
	list_filter = ('date_question',)
	ordering = ('-date_question', '-id')
	
admin.site.register(QuestionAnswerItem, QuestionAnswerItemAdmin)

################################################################################################################
################################################################################################################