# -*- coding: utf-8 -*-

from django.db import connection, models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
import datetime

################################################################################################################
################################################################################################################

#Загрузчик
class ExelParserUploader(models.Model):
	title = models.CharField(max_length=500, verbose_name=_('title'))
	callback = models.CharField(max_length=500, verbose_name=_('callback function'), help_text=_('example: exelparser.callback.exel_parser_test'))
	sort = models.IntegerField(verbose_name=_('sort'), default=0)
	
	def __unicode__(self):
		return self.title
			
	class Meta: 
		verbose_name = _('exel uploader') 
		verbose_name_plural = _('exel uploaders')
		ordering = ['sort', '-id']
		
################################################################################################################
################################################################################################################

STATUS = (
	('0', _('Expects')),
	('1', _('In work')),
	('2', _('Done')),
)
		
#Файл
class ExelParserFile(models.Model):
	uploader = models.ForeignKey(ExelParserUploader, verbose_name=_('uploader'))
	file = models.FileField(max_length=500, upload_to='upload/parsers/exelparser/', verbose_name=_('file'), help_text=_('.xls'))
	k = models.FloatField (verbose_name=_('multiplied by'), default=1.15)
	is_default = models.BooleanField(verbose_name=_('in default'), default=True, help_text=_('Upload in the default category.'))
	status = models.CharField(max_length=10, choices=STATUS, verbose_name=_("status parserfile"))
	errors = models.TextField(max_length=100000, verbose_name=_("errors"), blank=True)
	
	def __unicode__(self):
		return u'#%d' % self.id
		
	def get_info(self):
		info, create = ExelParserInfo.objects.get_or_create(parserfile=self)
		return info
		
	def at_create(self):
		if self.id and self.get_info().date_create:
			return self.get_info().date_create.strftime('%Y-%m-%d')
		return _('Unknown')
	at_create.short_description = _("At create")
	at_create.allow_tags = True
		
	def get_date_start(self):
		if self.id and self.get_info().date_start:
			return self.get_info().date_start.strftime('%Y-%m-%d')
		return _('Unknown')
	get_date_start.short_description = _("Start date")
	get_date_start.allow_tags = True
	
	def get_date_end(self):
		if self.id and self.get_info().date_end:
			return self.get_info().date_end.strftime('%Y-%m-%d')
		return _('Unknown')
	get_date_end.short_description = _("Start end")
	get_date_end.allow_tags = True
	
	def get_count_update_product(self):
		if self.id:
			if self.get_info().count_update_product > 0:
				return u'%d (<a target="_blank" href="/admin/shop/product/?id_exelparser=%d&status_exelparser=2&is_last_exelparser=1">%s</a>)' % (self.get_info().count_update_product, self.uploader.id, _('open list'))
			return u'0'
		return _('Unknown')
	get_count_update_product.short_description = _("Update product")
	get_count_update_product.allow_tags = True
	
	def get_count_create_product(self):
		if self.id:
			if self.get_info().count_create_product > 0:
				return u'%d (<a target="_blank" href="/admin/shop/product/?id_exelparser=%d&status_exelparser=1&is_last_exelparser=1">%s</a>)' % (self.get_info().count_create_product, self.uploader.id, _('open list'))
			return u'0'
		return _('Unknown')
	get_count_create_product.short_description = _("Create product")
	get_count_create_product.allow_tags = True
	
	def get_count_product_not_in_price(self):
		if self.id:
			if self.get_info().count_product_not_in_price > 0:
				return u'%d (<a target="_blank" href="/admin/shop/product/?is_last_exelparser=0">%s</a>)' % (self.get_info().count_product_not_in_price, _('open list'))
			return u'0'
		return _('Unknown')
	get_count_product_not_in_price.short_description = _("Product not in price")
	get_count_product_not_in_price.allow_tags = True
	
	def get_count_last_1_week(self):
		if self.id:
			if self.get_info().count_last_1_week > 0:
				gte = (datetime.datetime.now()-datetime.timedelta(days=14)).strftime('%Y-%m-%d')
				lt = (datetime.datetime.now()-datetime.timedelta(days=7)).strftime('%Y-%m-%d')
				return u'%d (<a target="_blank" href="/admin/shop/product/?date_exelparser__gte=%s&date_exelparser__lt=%s">%s</a>)' % (self.get_info().count_last_1_week, gte, lt, _('open list'))
			return u'0'
		return _('Unknown')
	get_count_last_1_week.short_description = _("Last 1 week")
	get_count_last_1_week.allow_tags = True
	
	def get_count_last_2_week(self):
		if self.id:
			if self.get_info().count_last_2_week > 0:
				gte = (datetime.datetime.now()-datetime.timedelta(days=30)).strftime('%Y-%m-%d')
				lt = (datetime.datetime.now()-datetime.timedelta(days=14)).strftime('%Y-%m-%d')
				return u'%d (<a target="_blank" href="/admin/shop/product/?date_exelparser__gte=%s&date_exelparser__lt=%s">%s</a>)' % (self.get_info().count_last_2_week, gte, lt, _('open list'))
			return u'0'
		return _('Unknown')
	get_count_last_2_week.short_description = _("Last 2 week")
	get_count_last_2_week.allow_tags = True
	
	def get_count_last_1_month(self):
		if self.id:
			if self.get_info().count_last_1_month > 0:
				gte = (datetime.datetime.now()-datetime.timedelta(days=60)).strftime('%Y-%m-%d')
				lt = (datetime.datetime.now()-datetime.timedelta(days=30)).strftime('%Y-%m-%d')
				return u'%d (<a target="_blank" href="/admin/shop/product/?date_exelparser__gte=%s&date_exelparser__lt=%s">open list</a>)' % (self.get_info().count_last_1_month, gte, lt, _('open list'))
			return u'0'
		return _('Unknown')
	get_count_last_1_month.short_description = _("Last 1 month")
	get_count_last_1_month.allow_tags = True
	
	def get_count_last_2_month(self):
		if self.id:
			if self.get_info().count_last_2_month > 0:
				lt = (datetime.datetime.now()-datetime.timedelta(days=60)).strftime('%Y-%m-%d')
				return u'%d (<a target="_blank" href="/admin/shop/product/?date_exelparser__lt=%s">%s</a>)' % (self.get_info().count_last_2_month, lt, _('open list'))
			return u'0'
		return _('Unknown')
	get_count_last_2_month.short_description = _("Last 2 month")
	get_count_last_2_month.allow_tags = True
		
	def get_status(self):
		if self.status == '2': return u'<img src="/media/admin/img/admin/icon-yes.gif"/> %s' % self.get_status_display()
		return self.get_status_display()
	get_status.short_description = _("Status")
	get_status.allow_tags = True
		
	class Meta: 
		verbose_name = _('exel file') 
		verbose_name_plural = _('exel files')
		ordering = ['-id']
		
	def save(self, *args, **kwargs):
		if not self.id:
			self.status = '0'
		else:
			info = self.get_info()
		
			if self.status == '1':
				info.date_start = datetime.datetime.now()
				info.save()
				
			if self.status == '2':
				info.date_end = datetime.datetime.now()
				info.save()
				
		super(ExelParserFile, self).save(*args, **kwargs)
		
def create_parser_info(sender, instance, created, **kwargs):   
	if created:
		info, created = ExelParserInfo.objects.get_or_create(parserfile=instance)   
 
post_save.connect(create_parser_info, sender=ExelParserFile)

################################################################################################################
################################################################################################################

#Информация
class ExelParserInfo(models.Model):
	parserfile = models.OneToOneField(ExelParserFile, primary_key=True)
	
	date_create = models.DateTimeField(default=datetime.datetime.now())
	date_start = models.DateTimeField(blank=True, null=True)
	date_end = models.DateTimeField(blank=True, null=True)
	
	count_update_product = models.IntegerField(default=0)
	count_create_product = models.IntegerField(default=0)
	
	count_product_not_in_price = models.IntegerField(default=0)
	
	count_last_1_week = models.IntegerField(default=0)
	count_last_2_week = models.IntegerField(default=0)
	count_last_1_month = models.IntegerField(default=0)
	count_last_2_month = models.IntegerField(default=0)
	
	def __unicode__(self):
		return u'%s' % _('ExelParserInfo')

################################################################################################################
################################################################################################################