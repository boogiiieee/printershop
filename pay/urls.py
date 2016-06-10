# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *


urlpatterns = patterns('pay.views',
	url(r'^callback/$', 'pay_callback'),
)