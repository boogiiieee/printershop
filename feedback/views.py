# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext, loader, RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.views.generic import list_detail
import datetime
import settings
import threading

from feedback.models import FeedBackItem
from feedback.forms import FeedBackForm
from shop.helper import letter_send_mail


################################################################################################################
################################################################################################################

def feedback_views(request, template, extra_context=None, context_processors=None, template_loader=loader):
	if request.method == 'POST':
		i = FeedBackItem(date=datetime.datetime.now())
		form = FeedBackForm(request.POST, instance=i)
		if form.is_valid():
			form.save()
			
			current_site = Site.objects.get_current()
			domain = current_site.domain
			
			users = User.objects.filter(is_staff=True, is_active=True)
			emails = [u.email for u in users]
			
			letter_send_mail(
				'mail/feedback.html',
				_('New message in %s.') % domain, emails, {'obj':i, 'domain':domain}
			)
			
			messages.add_message(request, messages.INFO, _("Thanks letter send."))
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		form = FeedBackForm()
		
	c = RequestContext(request, {'form':form}, context_processors)
	
	if extra_context:
		for key, value in extra_context.items():
			if callable(value): c[key] = value()
			else: c[key] = value
			
	t = template_loader.get_template(template)
	return HttpResponse(t.render(c))
	
################################################################################################################
################################################################################################################