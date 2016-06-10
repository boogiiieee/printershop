# -*- coding: utf-8 -*-

from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
import settings
import os, re
import datetime

from parsers.exelparser.models import ExelParserUploader, ExelParserInfo, ExelParserFile
	
#######################################################################################################################
#######################################################################################################################

class Command(NoArgsCommand):
	help = "Execute the exelparser's task"

	def handle_noargs(self, **options):
		for f in ExelParserFile.objects.filter(status='0'):
			f.status = '1'
			f.save()
			
			i = f.get_info()
			
			########################################################################################################
			
			extra_context_date = {
				'gte1': datetime.datetime.now()-datetime.timedelta(days=14),
				'lt1': datetime.datetime.now()-datetime.timedelta(days=7),
				'gte2': datetime.datetime.now()-datetime.timedelta(days=30),
				'lt2': datetime.datetime.now()-datetime.timedelta(days=14),
				'gte3': datetime.datetime.now()-datetime.timedelta(days=60),
				'lt3': datetime.datetime.now()-datetime.timedelta(days=30),
				'lt4': datetime.datetime.now()-datetime.timedelta(days=60),
			}
			
			########################################################################################################
			
			import xlrd
			try: rb = xlrd.open_workbook(file_contents=f.file.read())
			except:
				f.errors += u'%s' % _("Error open file.\n")
				f.save()
			else: sheet = rb.sheet_by_index(0)
			
			try:
				cb = str(f.uploader.callback).split('.')
				cb_function = cb[-1]
				cb_import = 'from ' + '.'.join(cb[:-1]) + ' import ' + cb_function
			except:
				f.errors += u'%s' % _("Error path callback function.\n")
				f.save()
			else:
				try: exec(cb_import)
				except:
					f.errors += u'%s' % _("Error import callback function.\n")
					f.save()
				else:
					########################################################################################################
					
					from shop.models import Product
					ps = Product.objects.all()
					ps.update(is_last_exelparser=False)
					
					########################################################################################################
					
					rows = []
					for rownum in range(sheet.nrows):
						try: 
							exec('errors=' + cb_function + '(sheet.row_values(rownum), f.k, f.is_default, f)')
						except:
							f.errors += u'%s' % _("Callback function not execute.\n")
							f.save()
						else:
							if errors:
								for error in errors:
									f.errors += u'%s' % _("'%s' not added.\n") % error
								f.save()
								
					########################################################################################################
					
					i.count_update_product = ps.filter(id_exelparser=f.uploader.id, status_exelparser=2, is_last_exelparser=True).count()
					i.count_create_product = ps.filter(id_exelparser=f.uploader.id, status_exelparser=1, is_last_exelparser=True).count()
					i.count_product_not_in_price = ps.count() - ps.filter(is_last_exelparser=True).count()
					
					i.count_last_1_week = ps.filter(Q(date_exelparser__gte=extra_context_date['gte1']) & Q(date_exelparser__lt=extra_context_date['lt1'])).count()
					i.count_last_2_week = ps.filter(Q(date_exelparser__gte=extra_context_date['gte2']) & Q(date_exelparser__lt=extra_context_date['lt2'])).count()
					i.count_last_1_month = ps.filter(Q(date_exelparser__gte=extra_context_date['gte3']) & Q(date_exelparser__lt=extra_context_date['lt3'])).count()
					i.count_last_2_month = ps.filter(date_exelparser__lt=extra_context_date['lt4']).count()
					
					i.save()
					
					########################################################################################################
					
					f.errors += u'%s' % _("Exel parser done.\n")
					f.status = '2'
					f.save()

#######################################################################################################################
#######################################################################################################################
