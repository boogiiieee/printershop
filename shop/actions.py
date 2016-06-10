# -*- coding: utf-8 -*-

from django.http import HttpResponseBadRequest, HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from django.contrib import admin
from django.db.models import Q
import settings
import datetime

from shop.forms import ChangeCategoryForm, SendMessageActionForm
from shop.helper import letter_send_mail

##################################################################################################	
##################################################################################################

#Изменить категорию товара
def ChangeCategoryAction(modeladmin, request, queryset):
	form = None
	if 'apply' in request.POST:
		form = ChangeCategoryForm(request.POST)

		if form.is_valid():
			c = form.cleaned_data['category']
			
			count = 0
			for pr in queryset:
				pr.category = c
				pr.save()
				count += 1

			modeladmin.message_user(request, _('Products count %(count)d changed category %(category)s.') % {'category':c.title, 'count':count})
			return HttpResponseRedirect(request.get_full_path())

	if not form:
		form = ChangeCategoryForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

	return render_to_response('shop/actions/simple_action.html', {'action':'ChangeCategoryAction', 'items':queryset, 'form':form, 'title':_('Change category')}, RequestContext(request))

ChangeCategoryAction.short_description = _('Change category')

##################################################################################################	
##################################################################################################

#Отправить сообщение пользователям-заказчикам
def SendMessageAction(modeladmin, request, queryset):
	form = None
	if 'apply' in request.POST:
		form = SendMessageActionForm(request.POST)

		if form.is_valid():
			text = form.cleaned_data['text']
			
			current_site = Site.objects.get_current()
			domain = current_site.domain
			
			emails = []
			
			count = 0
			for o in queryset:
				if o.email and not o.email in emails:
					emails.append(o.email)

					letter_send_mail(
						'mail/send_message_action.html',
						_('Message from the site %s.') % domain, [o.email], {'obj':o, 'text':text, 'domain':domain}
					)
					count += 1

			modeladmin.message_user(request, _('Message is sent to %d users.') % count)
			return HttpResponseRedirect(request.get_full_path())

	if not form:
		form = SendMessageActionForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

	return render_to_response('shop/actions/simple_action.html', {'action':'SendMessageAction', 'items':queryset, 'form':form, 'title':_('Send message')}, RequestContext(request))

SendMessageAction.short_description = _('Send message')

##################################################################################################	
##################################################################################################