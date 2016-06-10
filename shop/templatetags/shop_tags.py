# -*- coding: utf-8 -*-

from django import template
from django.template import Node, NodeList, Template, Context, Variable
from django.template import TemplateSyntaxError
from django.template import get_library, Library, InvalidTemplateLibrary
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from django.db.models import Avg, Max, Min, Count, Sum
from django.utils.encoding import force_unicode
import settings
import os
import re

from shop.models import Category, Printer, Product, Order
from shop.forms import SearchMinForm, SearchForm

register = template.Library()

#######################################################################################################################
#######################################################################################################################

#Возвращает товар по id	
class ShopPrductByIdNode(Node):
	def __init__(self, varname, id):
		self.varname = varname
		self.id = id
		
	def render(self, context):
		context[self.varname] = Product.objects.get(id=template.Variable(self.id).resolve(context), is_active=True)
		return ''

def ShopPrductById(parser, token):
	bits = token.split_contents()
	if len(bits) != 3: raise TemplateSyntaxError(_('Error token tag "ShopPrductById"'))
	return ShopPrductByIdNode(bits[1][1:-1], bits[2])

register.tag('ShopPrductById', ShopPrductById)

#######################################################################################################################
#######################################################################################################################

#Подключает корзину
class ShopBasketMinNode(Node):
	def __init__(self):
		pass

	def render(self, context):
		b, create = Order.objects.get_or_create(session=context['request'].shop_session, is_history=False)
		return render_to_response('shop/basket/basket-min.html', {'count':b.get_total_count()})._get_content()

def ShopBasketMin(parser, token):
	bits = token.split_contents()
	if len(bits) > 1: raise TemplateSyntaxError(_('Error token tag "ShopBasketMin"'))
	return ShopBasketMinNode()

register.tag('ShopBasketMin', ShopBasketMin)

#######################################################################################################################
#######################################################################################################################

#Простая форма поиска товара в контекст
class ShopSearchMinNode(Node):
	def __init__(self, varname):
		self.varname = varname
		
	def render(self, context):
		initial = {}
		if 'q' in context['request'].GET: initial['q'] = context['request'].GET.get('q')
		context[self.varname] = SearchMinForm(initial=initial)
		return ''

def ShopSearchMin(parser, token):
	bits = token.split_contents()
	if len(bits) != 2: raise TemplateSyntaxError(_('Error token tag "ShopSearchMin"'))
	return ShopSearchMinNode(bits[1][1:-1])

register.tag('ShopSearchMin', ShopSearchMin)

#######################################################################################################################
#######################################################################################################################

#Расширенная форма поиска товара в контекст
class ShopSearchNode(Node):
	def __init__(self, varname):
		self.varname = varname
		
	def render(self, context):
		initial = {}
		
		if 'c' in context['request'].GET: initial['c'] = context['request'].GET.get('c')
		if 'p' in context['request'].GET: initial['p'] = context['request'].GET.get('p')
		if 'q' in context['request'].GET: initial['q'] = context['request'].GET.get('q')
		
		if 'c' in initial.keys() and initial['c']:
			context[self.varname] = SearchForm(initial=initial, cat=initial['c'])
		else:
			context[self.varname] = SearchForm(initial=initial)
			
		return ''

def ShopSearch(parser, token):
	bits = token.split_contents()
	if len(bits) != 2:
		raise TemplateSyntaxError(_('Error token tag "ShopSearch"'))
	return ShopSearchNode(bits[1][1:-1])

register.tag('ShopSearch', ShopSearch)

#######################################################################################################################
#######################################################################################################################

#Список категорий в контекст
class ShopGetCategoryNode(Node):
	def __init__(self, varname):
		self.varname = varname
		
	def render(self, context):
		context[self.varname] = Category.tree.root_nodes().filter(is_active=True)
		return ''

def ShopGetCategory(parser, token):
	bits = token.split_contents()
	if len(bits) != 2: raise TemplateSyntaxError(_('Error token tag "ShopGetCategory"'))
	return ShopGetCategoryNode(bits[1][1:-1])

register.tag('ShopGetCategory', ShopGetCategory)

#######################################################################################################################
#######################################################################################################################

class get_url_node(Node):
	def __init__(self, opt, val, com, v):
		self.opt = opt
		self.val = val
		
		self.com = com
		self.v = v

	def render(self, context):
		g = context['request'].GET
		u = g.urlencode()
		
		if self.com == 'delete-key' and self.v:
			if u:
				e = g.copy()
				if self.v in e.keys():
					del e[self.v]
					g = e
					
		u = g.urlencode()
		
		try:
			val = template.Variable(self.val).resolve(context)
			if val == 'none':
				if u:
					e = g.copy()
					if self.opt in u: del e[self.opt]
					return u'?%s' % e.urlencode()
				else: return u''
		except: val = self.val
			
		if u:
			if self.opt in u:
				if val == g.get(self.opt): return u'?%s' % u
				else:
					e = g.copy()
					e[self.opt] = val
					return u'?%s' % e.urlencode()
			else: return u'?%s&%s=%s' % (u, self.opt, val)
		else: return u'?%s=%s' % (self.opt, val)
		
def get_url(parser, token):
	bits = token.split_contents()
	if len(bits) < 3:
		raise TemplateSyntaxError(_('Error token tag "get_url"'))
		
	try:
		com = bits[3][1:-1]
		var = bits[4]
	except:
		com = None
		var = None
		
	return get_url_node(bits[1][1:-1], bits[2], com, var)
	
get_url = register.tag(get_url)

#######################################################################################################################
#######################################################################################################################

@register.filter(name='equal_in_get')
def equal_in_get(x, y):
	try: x = int(x)
	except: pass
	try: y = int(y)
	except: pass
	if x == y: return True
	return False
		
#######################################################################################################################
#######################################################################################################################

@register.filter(name='mult')
def mult(x, y):
	try:
		x = int(x)
		y = int(y)
	except: return u'-'
	if x*y < 1: return u'-'
	return x*y
		
#######################################################################################################################
#######################################################################################################################

def shop_intcomma(value, exploder=' '):
    """
    Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3 000' and 45000 becomes '45 000'.
    """
    orig = force_unicode(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>%s\g<2>' % exploder, orig)
    if orig == new: return new
    else: return shop_intcomma(new)
	
shop_intcomma.is_safe = True
register.filter(shop_intcomma)

#######################################################################################################################
#######################################################################################################################