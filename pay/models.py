# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
import datetime

from shop.models import Order

################################################################################################################
################################################################################################################

CURRENCY_TYPE = (
	(u'4', u'AFA'),
	(u'8', u'ALL'),
	(u'12', u'DZD'),
	(u'20', u'ADP'),
	(u'31', u'AZM'),
	(u'32', u'ARS'),
	(u'36', u'AUD'),
	(u'44', u'BSD'),
	(u'48', u'BHD'),
	(u'50', u'BDT'),
	(u'51', u'AMD'),
	(u'52', u'BBD'),
	(u'60', u'BMD'),
	(u'64', u'BTN'),
	(u'68', u'BOB'),
	(u'72', u'BWP'),
	(u'84', u'BZD'),
	(u'90', u'SBD'),
	(u'96', u'BND'),
	(u'100', u'BGL'),
	(u'104', u'MMK'),
	(u'108', u'BIF'),
	(u'116', u'KHR'),
	(u'124', u'CAD'),
	(u'132', u'CVE'),
	(u'136', u'KYD'),
	(u'144', u'LKR'),
	(u'152', u'CLP'),
	(u'156', u'CNY'),
	(u'170', u'COP'),
	(u'174', u'KMF'),
	(u'188', u'CRC'),
	(u'191', u'HRK'),
	(u'192', u'CUP'),
	(u'196', u'CYP'),
	(u'203', u'CZK'),
	(u'208', u'DKK'),
	(u'214', u'DOP'),
	(u'218', u'ECS'),
	(u'222', u'SVC'),
	(u'230', u'ETB'),
	(u'232', u'ERN'),
	(u'233', u'EEK'),
	(u'238', u'FKP'),
	(u'242', u'FJD'),
	(u'262', u'DJF'),
	(u'270', u'GMD'),
	(u'288', u'GHC'),
	(u'292', u'GIP'),
	(u'320', u'GTQ'),
	(u'324', u'GNF'),
	(u'328', u'GYD'),
	(u'332', u'HTG'),
	(u'340', u'HNL'),
	(u'344', u'HKD'),
	(u'348', u'HUF'),
	(u'352', u'ISK'),
	(u'356', u'INR'),
	(u'360', u'IDR'),
	(u'364', u'IRR'),
	(u'368', u'IQD'),
	(u'376', u'ILS'),
	(u'388', u'JMD'),
	(u'392', u'JPY'),
	(u'398', u'KZT'),
	(u'400', u'JOD'),
	(u'404', u'KES'),
	(u'408', u'KPW'),
	(u'410', u'KRW'),
	(u'414', u'KWD'),
	(u'417', u'KGS'),
	(u'418', u'LAK'),
	(u'422', u'LBP'),
	(u'426', u'LSL'),
	(u'428', u'LVL'),
	(u'430', u'LRD'),
	(u'434', u'LYD'),
	(u'440', u'LTL'),
	(u'446', u'MOP'),
	(u'450', u'MGF'),
	(u'454', u'MWK'),
	(u'458', u'MYR'),
	(u'462', u'MVR'),
	(u'470', u'MTL'),
	(u'478', u'MRO'),
	(u'480', u'MUR'),
	(u'484', u'MXN'),
	(u'496', u'MNT'),
	(u'498', u'MDL'),
	(u'504', u'MAD'),
	(u'508', u'MZM'),
	(u'512', u'OMR'),
	(u'516', u'NAD'),
	(u'524', u'NPR'),
	(u'532', u'ANG'),
	(u'533', u'AWG'),
	(u'548', u'VUV'),
	(u'554', u'NZD'),
	(u'558', u'NIO'),
	(u'566', u'NGN'),
	(u'578', u'NOK'),
	(u'586', u'PKR'),
	(u'590', u'PAB'),
	(u'598', u'PGK'),
	(u'600', u'PYG'),
	(u'604', u'PEN'),
	(u'608', u'PHP'),
	(u'624', u'GWP'),
	(u'626', u'TPE'),
	(u'634', u'QAR'),
	(u'642', u'ROL'),
	(u'643', u'RUB'),
	(u'646', u'RWF'),
	(u'654', u'SHP'),
	(u'678', u'STD'),
	(u'682', u'SAR'),
	(u'690', u'SCR'),
	(u'694', u'SLL'),
	(u'702', u'SGD'),
	(u'703', u'SKK'),
	(u'704', u'VND'),
	(u'705', u'SIT'),
	(u'706', u'SOS'),
	(u'710', u'ZAR'),
	(u'716', u'ZWD'),
	(u'736', u'SDD'),
	(u'740', u'SRG'),
	(u'748', u'SZL'),
	(u'752', u'SEK'),
	(u'756', u'CHF'),
	(u'760', u'SYP'),
	(u'764', u'THB'),
	(u'776', u'TOP'),
	(u'780', u'TTD'),
	(u'784', u'AED'),
	(u'788', u'TND'),
	(u'792', u'TRL'),
	(u'795', u'TMM'),
	(u'800', u'UGX'),
	(u'807', u'MKD'),
	(u'810', u'RUR'),
	(u'818', u'EGP'),
	(u'826', u'GBP'),
	(u'834', u'TZS'),
	(u'840', u'USD'),
	(u'858', u'UYU'),
	(u'860', u'UZS'),
	(u'862', u'VEB'),
	(u'886', u'YER'),
	(u'891', u'YUM'),
	(u'894', u'ZMK'),
	(u'901', u'TWD'),
	(u'949', u'TRY'),
	(u'950', u'XAF'),
	(u'951', u'XCD'),
	(u'952', u'XOF'),
	(u'953', u'XPF'),
	(u'972', u'TJS'),
	(u'973', u'AOA'),
	(u'974', u'BYR'),
	(u'975', u'BGN'),
	(u'976', u'CDF'),
	(u'977', u'BAM'),
	(u'978', u'EUR'),
	(u'979', u'MXV'),
	(u'980', u'UAH'),
	(u'981', u'GEL'),
	(u'983', u'ECV'),
	(u'984', u'BOV'),
	(u'985', u'PLN'),
	(u'986', u'BRL'),
	(u'990', u'CLF'),
)

PAYMENT_TYPE = (
	(u'1', u'Dankort/VISA Dankort'),
	(u'2', u'eDankort'),
	(u'3', u'VISA/VISA Electron'),
	(u'4', u'Mastercard'),
	(u'6', u'JCB'),
	(u'7', u'Maestro'),
	(u'8', u'Diners Club'),
	(u'9', u'American Express'),
	(u'11', u'Forbrugsforeningen'),
	(u'12', u'Nordea e-betaling'),
	(u'13', u'Danske Netbetalinger'),
	(u'14', u'PayPal'),
	(u'15', u'MobilPenge'),
)

class Pay(models.Model):
	merchantnumber = models.CharField(max_length=20, verbose_name=_("merchantnumber")) #ApiKey
	
	currency = models.CharField(max_length=10, verbose_name=_("currency"), choices=CURRENCY_TYPE, blank=True) #Валюта
	amount = models.CharField(max_length=10, verbose_name=_("amount"), blank=True) #Оплаченная сумма
	
	txnid = models.CharField(max_length=20, verbose_name=_("id transaction"), blank=True) #Id транзакции
	orderid = models.CharField(max_length=20, verbose_name=_("id order")) #Id платежа
	txnfee = models.CharField(max_length=10, verbose_name=_("fee"), blank=True) #За операцию (в незначительных единиц) добавляется к клиенту
	paymenttype = models.CharField(max_length=10, verbose_name=_("payment type"), choices=PAYMENT_TYPE, blank=True) #Чем оплатил
	
	date = models.DateTimeField(verbose_name=_("date"), blank=True, null=True)
	hash = models.CharField(max_length=100, verbose_name=_("hash"))
	is_paid = models.BooleanField(verbose_name=_('is paid'), blank=True)
	
	shop_order = models.ForeignKey(Order, verbose_name=_('order in shop'))
	
	def __unicode__(self):
		return self.orderid
		
	class Meta: 
		verbose_name = _("pay") 
		verbose_name_plural = _("pays")
		ordering = ['-id']
		
	def get_link(self):
		return _('<a href="https://ssl.ditonlinebetalingssystem.dk/admin/transactions_info.asp?tid=%s" target="_blank">Show in Epay</a>') % self.txnid
	get_link.short_description = _("Link")
	get_link.allow_tags = True
	
	def get_order(self):
		return _('<a href="/admin/shop/order/%(id)d/">Show order #%(id)d in shop</a>') % {'id':self.shop_order.id}
	get_order.short_description = _("Order")
	get_order.allow_tags = True
		
################################################################################################################
################################################################################################################