# -*- coding: utf-8 -*-

from django.http import HttpResponse
import hashlib
import datetime
import re
import os

from pay.models import Pay
from pay.conf import settings

#######################################################################################################################
#######################################################################################################################

def pre_pay(order, useramount):
	orderid = str(order.id)
	
	params = {
		'merchantnumber': settings.MERCHANT_NUMBER,
		'currency': settings.CURRENCY,
		'windowstate': settings.WINDOWSTATE,
		'paymentcollection': settings.PAYMENT_COLLECTION,
		'language': settings.LANGUAGE,
		'windowid': settings.WINDOWID,
		'orderid': orderid,
		'useramount': int(useramount),
		'accepturl': settings.ACCEPT_URL,
		'cancelurl': settings.CANCEL_URL,
	}
	
	hashstr = u''
	for key, value in params.items():
		hashstr += u'%s' % str(value)
	hashstr += settings.SOLT

	m = hashlib.md5()
	m.update(hashstr.encode('utf-8'))
	hash = m.hexdigest().decode('utf-8')
	
	params['hash'] = hash
	
	Pay.objects.get_or_create(
		merchantnumber = settings.MERCHANT_NUMBER,
		currency = settings.CURRENCY,
		amount = str(useramount),
		orderid = orderid,
		shop_order = order,
		hash = hash
	)
	
	return params

#######################################################################################################################
#######################################################################################################################

def get_pay(orderid):
	try: p = Pay.objects.get(orderid=orderid)
	except: return False
	else: return p

#######################################################################################################################
#######################################################################################################################

def pay_callback(request):
	from urlparse import urlparse
	q = urlparse(request.get_full_path())

	hashstr = u''
	for x in q.query.split(u'&'):
		key, value = x.split(u'=')
		if not key == u'hash':
			hashstr += u'%s' % value
	hashstr += settings.SOLT

	m = hashlib.md5()
	m.update(hashstr.encode('utf-8'))
	hash = m.hexdigest().decode('utf-8')
	
	if hash == request.GET.get('hash') and 'orderid' in request.GET:
		try: p = Pay.objects.get(orderid=request.GET.get('orderid'))
		except: pass
		else:
			p.is_paid = True
			p.shop_order.is_paid = True
			p.save()
			p.shop_order.save()
				
			if 'currency' in request.GET:
				p.currency = request.GET.get('currency')
			if 'amount' in request.GET:
				p.amount = request.GET.get('amount')
			if 'txnid' in request.GET:
				p.txnid = request.GET.get('txnid')
			if 'txnfee' in request.GET:
				p.txnfee = request.GET.get('txnfee')
			if 'paymenttype' in request.GET:
				p.paymenttype = request.GET.get('paymenttype')
			p.save()

	return HttpResponse(status=200)