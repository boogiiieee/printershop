# -*- coding: utf-8 -*-

from django import template
from django.template import Node, NodeList, Template, Context, Variable
from django.template import TemplateSyntaxError
from django.template import Library
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
import settings
import os
import re

from pay.views import pre_pay

register = template.Library()

#######################################################################################################################
#######################################################################################################################

#Возвращает ссылку на оплату товара
class GetPayLinkNode(Node):
	def __init__(self, order):
		self.order = order
		
	def render(self, context):
		order = template.Variable(self.order).resolve(context)
		params = pre_pay(order, order.get_total_cost())
		context['PaySubmitJS'] = 'startPayment()'
		return render_to_response('pay/pay.html', {'params':params})._get_content()

def GetPayLink(parser, token):
	bits = token.split_contents()
	if len(bits) != 2: raise TemplateSyntaxError(_('Error token tag "GetPayLink"'))
	return GetPayLinkNode(bits[1])

register.tag('GetPayLink', GetPayLink)

#######################################################################################################################
#######################################################################################################################