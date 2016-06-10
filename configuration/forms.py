# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
import re

from configuration.models import ConfigModel

class ConfigForm(forms.ModelForm):
	class Meta:
		model = ConfigModel