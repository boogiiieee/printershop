# -*- coding: utf-8 -*-

from django import template
from django.template import Node, NodeList, Template, Context, Variable
from django.template import TemplateSyntaxError
from django.template import get_library, Library, InvalidTemplateLibrary
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
import settings
import os
import re

from actions.models import ActionArticle

register = template.Library()

#######################################################################################################################
#######################################################################################################################

#Список акций в контекст
class ActionsGetItemNode(Node):
	def __init__(self, varname, count, exclude_id):
		self.varname = varname
		self.count = count
		self.exclude_id = exclude_id
		
	def render(self, context):
		items = ActionArticle.objects.filter(is_active=True)
		if self.exclude_id: items = items.exclude(id=template.Variable(self.exclude_id).resolve(context))
		context[self.varname] = items[0:self.count]
		return ''

def ActionsGetItem(parser, token):
	bits = token.split_contents()
	if len(bits) < 3: raise TemplateSyntaxError(_('Error token tag "ActionsGetItem"'))
	try: exclude_id = bits[3]
	except: exclude_id = None
	return ActionsGetItemNode(bits[1][1:-1], bits[2], exclude_id)

register.tag('ActionsGetItem', ActionsGetItem)

#######################################################################################################################
#######################################################################################################################