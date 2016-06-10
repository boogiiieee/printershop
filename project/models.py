# -*- coding: utf-8 -*-

from django.db import connection, models
from django.utils.translation import ugettext_lazy as _

################################################################################################################
################################################################################################################
		
#Перевод элементов интерфейса
class TranslateInterface(models.Model):
	name = models.CharField(max_length=500, verbose_name=_('name'))
	name_ru = models.CharField(max_length=500, verbose_name=_('name ru'))
	title = models.CharField(max_length=500, verbose_name=_('title'))
	
	def __unicode__(self):
		return self.name
			
	class Meta: 
		verbose_name = _('item') 
		verbose_name_plural = _('translate items')
		
	def save(self, *args, **kwargs):
		if not self.name_ru:
			self.name_ru = self.name
		super(TranslateInterface, self).save(*args, **kwargs)
		
################################################################################################################
################################################################################################################