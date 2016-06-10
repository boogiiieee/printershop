# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from tinymce import models as TinymceField
from sorl.thumbnail import ImageField as SorlImageField
from django.core.exceptions import ValidationError
import datetime
import re
import os

##########################################################################
##########################################################################

class ActionArticle(models.Model):
	title = models.CharField(max_length=100, verbose_name=_("title"))
	image = SorlImageField(upload_to=u'upload/action/', verbose_name=_("image"), blank=True, null=True, help_text=_("If exist flash then it has show."))
	flash = models.FileField(upload_to=u'upload/action/', verbose_name=_("flash"), help_text=_('Recommended size 250x150 px.'), blank=True, null=True)
	text = TinymceField.HTMLField(max_length=100000, verbose_name=_("text"))
	created_at = models.DateTimeField(verbose_name = _("date_created"), default=datetime.datetime.now())
	
	is_active = models.BooleanField(verbose_name=_("is_active"), default=True)
	sort = models.IntegerField(verbose_name=_("order"), default=0)
	
	def __unicode__(self):
		return u'%s' % self.title
		
	@models.permalink
	def get_absolute_url(self):
		return ('action_url', (), {})
		
	@models.permalink
	def get_item_url(self):
		return ('action_item_url', (), {'id': self.id})
		
	def clean(self):
		r = re.compile('^([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_-]+)$')
		if self.image:
			if not r.findall(os.path.split(self.image.url)[1]):
				raise ValidationError(_("File name validation error"))
		if self.flash:
			if not r.findall(os.path.split(self.flash.url)[1]):
				raise ValidationError(_("File name validation error"))
		
	class Meta: 
		verbose_name = _("action article")
		verbose_name_plural = _("actions")
		ordering = ['sort', '-created_at','-id']
		
##########################################################################
##########################################################################