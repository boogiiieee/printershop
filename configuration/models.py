# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

#######################################################################################################################
#######################################################################################################################

#Настройки
class ConfigModel(models.Model):
	organization = models.CharField(max_length=500, verbose_name=_('organization'), blank=True)
	
	phone1 = models.CharField(max_length=50, verbose_name=_('phone1'), blank=True, help_text=_("main phone"))
	phone2 = models.CharField(max_length=50, verbose_name=_('phone2'), blank=True)
	phone3 = models.CharField(max_length=50, verbose_name=_('phone3'), blank=True)
	
	icq1 = models.CharField(max_length=50, verbose_name=_('icq1'), blank=True, help_text=_("main icq"))
	icq2 = models.CharField(max_length=50, verbose_name=_('icq2'), blank=True)
	icq3 = models.CharField(max_length=50, verbose_name=_('icq3'), blank=True)
	
	office1 = models.CharField(max_length=200, verbose_name=_('office1'), blank=True, help_text=_("main office"))
	office2 = models.CharField(max_length=200, verbose_name=_('office2'), blank=True)
	office3 = models.CharField(max_length=200, verbose_name=_('office3'), blank=True)
	
	skype = models.CharField(max_length=100, verbose_name=_('skype'), blank=True)
	
	operating_time = models.CharField(max_length=50, verbose_name=_('operating time'), blank=True)
	
	mapx = models.CharField(max_length=50, verbose_name=_('mapx'), blank=True)
	mapy = models.CharField(max_length=50, verbose_name=_('mapy'), blank=True)
	
	cost_delivery = models.IntegerField(verbose_name=_('cost delivery'), default=0)
	free_delivery = models.IntegerField(verbose_name=_('free delivery'), default=2, help_text=_("of goods for free shipping"))
	
	requisites_org = models.CharField(max_length=100, verbose_name=_('requisites organization'), blank=True)
	requisites_adr = models.CharField(max_length=500, verbose_name=_('requisites address'), blank=True)
	requisites_phone = models.CharField(max_length=50, verbose_name=_('requisites phone'), blank=True)
	requisites_inn = models.CharField(max_length=50, verbose_name=_('requisites inn'), blank=True)
	requisites_bank = models.CharField(max_length=500, verbose_name=_('requisites bank'), blank=True)
	requisites_reg = models.CharField(max_length=50, verbose_name=_('requisites reg'), blank=True)
	requisites_acct = models.CharField(max_length=50, verbose_name=_('requisites acct'), blank=True)
	
	def __unicode__(self):
		return u'%s' % _("configuration")
		
	class Meta: 
		verbose_name = _("configuration") 
		verbose_name_plural = _("configurations")
		
#######################################################################################################################
#######################################################################################################################