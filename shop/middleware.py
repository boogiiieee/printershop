# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
import datetime
import uuid
	
#######################################################################################################################
#######################################################################################################################

class ShopSessionMiddleware(object):
	def process_request(self, request):
		if 'shop_session' in request.COOKIES: request.shop_session = request.COOKIES['shop_session']
		else: request.shop_session = str(uuid.uuid4())
		
	def process_response(self, request, response):
		if not 'shop_session' in request.COOKIES:
			if request.shop_session: ident = request.shop_session
			else: ident = str(uuid.uuid4())
			response.set_cookie("shop_session", ident, expires=datetime.date(3000,1,1).strftime("%a, %d-%b-%Y %H:%M:%S GMT"), path='/')
			request.__class__.shop_session = ident
		return response
		
#######################################################################################################################
#######################################################################################################################