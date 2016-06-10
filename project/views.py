# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext

from shop.views import shop_category, shop_product, shop_basket_ajax, shop_basket, shop_order, shop_order_thanks, shop_order_buy, shop_order_buy_thanks, shop_simple_search

################################################################################################################
################################################################################################################

#Главная
def index(request):
	return render_to_response('default.html', {'active':1}, RequestContext(request))

################################################################################################################
################################################################################################################


#Категории
def category(request):
	return shop_category(request, template='shop/category.html', extra_context={'active':2})
	
################################################################################################################
################################################################################################################

#Товары
def product(request, id, slug):
	return shop_product(request, id, template='shop/product.html', extra_context={'active':2, 'active2':int(id)})
	
################################################################################################################
################################################################################################################

#Поиск
def search(request):
	return shop_simple_search(request, template='shop/search.html', extra_context={'active':2})
	
################################################################################################################
################################################################################################################
	
#Мин. корзина
def basket_ajax(request):
	return shop_basket_ajax(request, template='shop/basket/basket-min.html')
	
################################################################################################################
################################################################################################################

#Корзина
def basket(request):
	return shop_basket(request, template='shop/basket/basket.html', extra_context={'active':3})
	
################################################################################################################
################################################################################################################
	
#Оформить заказ
def order(request):
	return shop_order(request, template='shop/basket/order.html', extra_context={'active':3})
	

#Спасибо за заказ + инфо о заказе
def order_thanks(request):
	return shop_order_thanks(request, template='shop/basket/order_thanks.html', extra_context={'active':3})

################################################################################################################
################################################################################################################

#Оплатить заказ
def order_buy(request):
	return shop_order_buy(request, template='shop/basket/buy.html', extra_context={'active':3})
	
#Спасибо за оплату + инфо о заказе
def order_buy_thanks(request):
	return shop_order_buy_thanks(request, template='shop/basket/buy_thanks.html', extra_context={'active':3})

################################################################################################################
################################################################################################################

from actions.views import all as actions_all, full as actions_full

#Акции
def actions(request):
	return actions_all(request, template_name='actions/actions.html', extra_context={'active':4})
	
#Акция
def action(request, id):
	return actions_full(request, id, template_name='actions/item.html', extra_context={'active':4})
	
################################################################################################################
################################################################################################################

from questionanswer.views import question_answer

#Вопрос-ответ
def faq(request):
	return question_answer(request, template='faq.html', extra_context={'active':5})
	
################################################################################################################
################################################################################################################

from feedback.views import feedback_views

def contacts(request):
	return feedback_views(request, template='contacts.html', extra_context={'active':6})

################################################################################################################
################################################################################################################