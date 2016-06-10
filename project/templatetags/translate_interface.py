# -*- coding: utf-8 -*-

from django import template

register = template.Library()

from project.models import TranslateInterface

##################################################################################################	
##################################################################################################

@register.filter(name='trans')
def trans(self, str):
	if not self:
		self = TranslateInterface.objects.all()
		
	x = None
	try: x = self.get_or_create(name=str)[0]
	except: pass
	
	if x:
		if x.title: return x.title
		else: return x.name
		
	return str
	
##################################################################################################	
##################################################################################################