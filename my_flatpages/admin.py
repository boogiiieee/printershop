# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from django.contrib.flatpages.models import FlatPage as oldFlatPage
from my_flatpages.models import FlatPage

################################################################################################################
################################################################################################################

class FlatpageForm(forms.ModelForm):
	url = forms.RegexField(label=_("URL"), max_length=100, regex=r'^[-\w/\.~]+$',
		help_text = _("Example: '/about/contact/'. Make sure to have leading"
			" and trailing slashes."),
		error_message = _("This value must contain only letters, numbers,"
			" dots, underscores, dashes, slashes or tildes."))

	class Meta:
		model = FlatPage

class FlatPageAdmin(admin.ModelAdmin):
	form = FlatpageForm
	fieldsets = (
		(None, {'fields': ('url', 'title', 'content', 'sites')}),
	)
	list_display = ('title', 'url')
	search_fields = ('title', 'url')
	
	def has_add_permission(self, request):
		return False
		
	def has_delete_permission(self, request, obj=None):
		return False

admin.site.unregister(oldFlatPage)
admin.site.register(FlatPage, FlatPageAdmin)

################################################################################################################
################################################################################################################