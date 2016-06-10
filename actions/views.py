# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.views.generic import list_detail, simple
import settings

from actions.models import ActionArticle

##########################################################################
##########################################################################

def all(request, template_name='actions/actions.html', extra_context=None):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except TypeError: raise Http404()
		
	objs = ActionArticle.objects.filter(is_active=True)
	
	return list_detail.object_list(
		request,
		queryset = objs,
		paginate_by = settings.PAGINATE_BY,
		page = page,
		template_name = template_name,
		template_object_name = 'actions',
		extra_context = extra_context,
	)
	
##########################################################################
##########################################################################
	
def full(request, id, template_name='actions/item.html', extra_context=None):
	try:
		id = int(id)
	except TypeError:
		raise Http404()
		
	objs = ActionArticle.objects.filter(is_active=True)
	
	return list_detail.object_detail(
		request,
		queryset = objs,
		object_id = id,
		template_name = template_name,
		extra_context = extra_context,
		template_object_name='action',
	)
	
##########################################################################
##########################################################################