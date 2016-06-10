# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from parsers.exelparser.models import ExelParserUploader, ExelParserInfo, ExelParserFile

################################################################################################################
################################################################################################################
	
class ExelParserUploaderAdmin(admin.ModelAdmin):
	list_display = ('title', 'sort')
	list_editable = ('sort',)
		
# admin.site.register(ExelParserUploader, ExelParserUploaderAdmin)

################################################################################################################
################################################################################################################
	
#Τΰιλ
class ExelParserFileAdmin(admin.ModelAdmin):
	list_display = ('file', 'uploader', 'k', 'is_default', 'at_create', 'get_status')
	fieldsets = (
		(None, {'fields': ('uploader', 'file', 'k', 'is_default', 'status', 'errors')}),
		(_('Additionally'), {'fields': (
			'get_date_start',
			'get_date_end',
			'get_count_update_product',
			'get_count_create_product',
			'get_count_product_not_in_price',
			'get_count_last_1_week',
			'get_count_last_2_week',
			'get_count_last_1_month',
			'get_count_last_2_month',
		)})
	)
	readonly_fields = (
		'status',
		'get_date_start',
		'get_date_end',
		'get_count_update_product',
		'get_count_create_product',
		'get_count_product_not_in_price',
		'get_count_last_1_week',
		'get_count_last_2_week',
		'get_count_last_1_month',
		'get_count_last_2_month',
	)
		
admin.site.register(ExelParserFile, ExelParserFileAdmin)
	
################################################################################################################
################################################################################################################