# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime
from django.http import HttpResponseRedirect, Http404

from admin_tools.dashboard.modules import DashboardModule

from configuration.models import ConfigModel
from configuration.forms import ConfigForm

#######################################################################################################################
#######################################################################################################################

class ConfigModule(DashboardModule):
	def is_empty(self):
		pass

	def __init__(self, **kwargs):
		super(ConfigModule, self).__init__(**kwargs)
		self.title = _('Configuration')
		self.template = 'blocks/configuration.html'

		c, create = ConfigModel.objects.get_or_create(id=1)
		self.form = ConfigForm(instance=c)
		
#######################################################################################################################
#######################################################################################################################

@login_required
def save_config(request):
	if request.user.is_superuser:
		if request.method == "POST":
			c, create = ConfigModel.objects.get_or_create(id=1)
			form = ConfigForm(request.POST, instance=c)
			if form.is_valid():
				form.save()
				messages.add_message(request, messages.INFO, _("Save form configuration."))
				return HttpResponseRedirect('/admin/')
		messages.add_message(request, messages.ERROR, _("Error save form configuration."))
		return HttpResponseRedirect('/admin/')
	raise Http404()