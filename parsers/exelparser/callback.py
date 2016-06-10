# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.utils.text import capfirst
import datetime
import re

import chardet

from shop.models import Category, Printer, Product

################################################################################################################
################################################################################################################

def exel_parser_1(cols, k, in_default, parser):
	errors = []
	
	if cols:
		try: cp = cols[0]
		except: return errors.append('Error 000001')
		else:
			if cp:
				try: title = cols[1]
				except: title = u''
				
				try: description = cols[2]
				except: description = u''
				
				try: cost = int(float(cols[3]) * float(k))
				except: cost = 0
				
				try: resource = cols[4]
				except: resource = u''
				
				category = None
				cats = Category.objects.all()
				if cats.count() > 0:
					for c in cats:
						if c.cod and re.findall(ur'^%s' % c.cod, str(cp)):
							category = c
							break
				else: errors.append(cp)
					
				if not category:
					if not in_default: return errors
					else:
						category = Category.objects.get_or_create(title=u'Andet', parent__isnull=True)[0]
				
				cp = cp.replace(category.cod, '').strip()
				
				printer = Printer.objects.get_or_create(title=cp)[0]
				if not printer: printer = None
				
				if title:
					#Сохранить продукт + информацию о парсере
					ps = Product.objects.filter(exelparser_title=title)
					if ps.count():
						for p in ps:
							if not p.is_checked:
								p.code = title
								if description: p.description = description
								if resource: p.resource = resource
							if cost and (p.cost > cost or p.cost == 0): p.cost = cost

							p.id_exelparser = parser.uploader.id
							p.is_last_exelparser = True
							p.status_exelparser = 2
							p.date_exelparser = datetime.datetime.now()
							p.exelparser = parser.uploader.title
							p.save()
					else:
						p = Product.objects.create(
							category = category, 
							printer = printer, 
							title = title, 
							code = title, 
							resource = resource, 
							description = description, 
							cost = cost, 
							exelparser_title = title,

							id_exelparser = parser.uploader.id,
							is_last_exelparser = True,
							status_exelparser = 1,
							date_exelparser = datetime.datetime.now(),
							exelparser = parser.uploader.title
						)
				else:
					errors.append(cp)
				
				return errors
	return False
	
################################################################################################################
################################################################################################################