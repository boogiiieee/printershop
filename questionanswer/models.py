# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from tinymce import models as TinymceField
import datetime

################################################################################################################
################################################################################################################

class QuestionAnswerItem(models.Model):
	name = models.CharField(max_length=100, verbose_name=_("name"))
	email = models.CharField(max_length=100, verbose_name=_("email"), blank=True)
	phone = models.CharField(max_length=100, verbose_name=_("phone"), blank=True)
	
	question = TinymceField.HTMLField(max_length=1000, verbose_name=_("question"))
	date_question = models.DateTimeField(verbose_name=_("date question"), default=datetime.datetime.now())
	
	name_answer = models.CharField(max_length=100, verbose_name=_("name answer"), blank=True)
	answer = TinymceField.HTMLField(max_length=1000, verbose_name=_("answer"), blank=True)
	date_answer = models.DateTimeField(verbose_name=_("date answer"), blank=True, null=True)
	
	is_active = models.BooleanField(verbose_name=_('is active'), default=False)
	sort = models.IntegerField(verbose_name=_('sort'), default=0)
	
	def __unicode__(self):
		return u'%s' % self.name
		
	class Meta: 
		verbose_name = _("item") 
		verbose_name_plural = _("question-answer")
		ordering = ['sort', '-date_question','-date_answer','-id']
		
################################################################################################################
################################################################################################################