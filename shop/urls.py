# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('shop.views',
	url(r'^shop/add/$', 'basket_add'),
	url(r'^shop/clean/$', 'basket_clean'),
	url(r'^shop/ajax/basket-min/$', 'ajax_basket_min'),
	
	url(r'^shop/plate/$', 'plate'),
	url(r'^shop/invoice/$', 'invoice'),
	
	url(r'^admin/shop/report/$', 'report'),
	url(r'^admin/shop/save_history/$', 'save_history'),
)