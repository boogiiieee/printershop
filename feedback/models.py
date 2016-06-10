# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from tinymce import models as TinymceField
import datetime

################################################################################################################
################################################################################################################

class FeedBackItem(models.Model):
	name = models.CharField(max_length=100, verbose_name=_("name"))
	email = models.CharField(max_length=100, verbose_name=_("email"), blank=True)
	phone = models.CharField(max_length=100, verbose_name=_("phone"), blank=True)
	
	text = TinymceField.HTMLField(max_length=1000, verbose_name=_("text"))
	date = models.DateTimeField(verbose_name=_("date"), default=datetime.datetime.now())
	
	def __unicode__(self):
		return u'%s' % self.name
		
	class Meta: 
		verbose_name = _("feedback item") 
		verbose_name_plural = _("feedback items")
		ordering = ['-date']
		
################################################################################################################
################################################################################################################