#coding: utf-8

import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _

################################################################################################################
################################################################################################################

#СМСки
class SmsModel(models.Model):
	SMS_STATUS = (
			('0', _('is sent')),
			('1', _('is deliver')),
			('2', _('is error')),
		)
	to = models.CharField(max_length=100, verbose_name=_("to"))
	text = models.TextField(max_length=500, verbose_name=_("text"))
	status = models.CharField(max_length=100, choices=SMS_STATUS, verbose_name=_("status"))
	date = models.DateTimeField(verbose_name=_('date'), default=datetime.datetime.now())
	
	def __unicode__(self):
		return u'%d / %s' % (self.id, self.to)
		
	def get_icon_status(self):
		if self.status == '1': return u'<img src="/media/admin/img/admin/icon-yes.gif"/>'
		elif self.status == '2': return u'<img src="/media/admin/img/admin/icon-no.gif"/>'
		else: return u'<img src="/media/admin/img/admin/icon-unknown.gif"/>'
			
	get_icon_status.short_description = _("Status")
	get_icon_status.allow_tags = True
			
	class Meta: 
		verbose_name = _('sms') 
		verbose_name_plural = _('smss')
		ordering = ['-id',]

################################################################################################################
################################################################################################################
