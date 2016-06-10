# -*- coding: utf-8 -*-

from django.contrib.admin.filterspecs import RelatedFilterSpec

################################################################################################################
################################################################################################################

#Сортировка пользовательского фильтра по названию
class SortTitleFilterSpec(RelatedFilterSpec):
	def __init__(self, f, request, params, model, model_admin, field_path=None):
		super(SortTitleFilterSpec, self).__init__(f, request, params, model, model_admin, field_path=field_path)
		self.lookup_choices = sorted(f.get_choices(include_blank=False),key=lambda x: x[1])
		
		
################################################################################################################
################################################################################################################