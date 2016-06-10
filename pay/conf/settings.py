# -*- coding: utf-8 -*-

from django.conf import settings

MERCHANT_NUMBER = getattr(settings, 'PAY_MERCHANT_NUMBER', u'8010472')
CURRENCY = getattr(settings, 'PAY_CURRENCY', u'208')
WINDOWSTATE = getattr(settings, 'PAY_WINDOWSTATE', 1)
PAYMENT_COLLECTION = getattr(settings, 'PAY_PAYMENT_COLLECTION', 1)
LANGUAGE = getattr(settings, 'PAY_LANGUAGE', 0)
WINDOWID = getattr(settings, 'PAY_WINDOWID', 1)
ACCEPT_URL = getattr(settings, 'PAY_ACCEPT_URL', u'http://laserpatrongenbrug.laserpatrongenbrug.locum.ru/basket/order/buy/thanks/')
CANCEL_URL = getattr(settings, 'PAY_CANCEL_URL', u'http://laserpatrongenbrug.laserpatrongenbrug.locum.ru/basket/order/buy/thanks/')
SOLT = getattr(settings, 'PAY_SOLT', u'lx39ue4gf5ki2c34u78')

#CALLBACK URL = '/pay/callback/'