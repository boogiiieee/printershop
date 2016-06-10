# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic import list_detail, simple
from django.conf import settings
from django.contrib.sitemaps import FlatPageSitemap

from shop.views import CategorySitemap

sitemaps = {
	'flatpages': FlatPageSitemap,
	'category':CategorySitemap,
}

urlpatterns = patterns('project.views',
	url(r'^$', 'index'),
	
	url(r'^catalog/$', 'category'),
	url(r'^(?P<id>[0-9]+)/(?P<slug>.+)/$', 'product', name='subcategory_url'),
	
	url(r'^basket/$', 'basket'),
	url(r'^basket/ajax/$', 'basket_ajax'),
	url(r'^basket/order/$', 'order'),
	url(r'^basket/order/thanks/$', 'order_thanks'),
	url(r'^basket/order/buy/$', 'order_buy'),
	url(r'^basket/order/buy/thanks/$', 'order_buy_thanks'),
	
	url(r'^search/$', 'search'),
	
	url(r'^actions/$', 'actions', name='action_url'),	
	url(r'^actions/(?P<id>[0-9]{1,4})/$', 'action', name='action_item_url'),
	url(r'^faq/$', 'faq'),
	url(r'^contacts/$', 'contacts'),
)

urlpatterns += patterns('',
	url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
	url(r'^robots\.txt$', 'django.views.static.serve', {'path':"/robots.txt", 'document_root':settings.MEDIA_ROOT, 'show_indexes': False}),
)