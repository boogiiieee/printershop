# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from captcha.fields import CaptchaField
from mptt.forms import TreeNodeChoiceField
import re

from shop.models import Category, Printer, Order, OrderProduct

##################################################################################################	
##################################################################################################

#Сменить категорию товара/Action
class ChangeCategoryForm(forms.Form):
	_selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
	category = TreeNodeChoiceField(queryset=Category.tree.filter(is_active=True), label=_('Category'))
	
#Отправить сообщение пользователям-заказчикам/Action
class SendMessageActionForm(forms.Form):
	_selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
	text = forms.CharField(label=_('Message'), widget=forms.Textarea())
	
##################################################################################################	
##################################################################################################

class SearchMinForm(forms.Form):
	q = forms.CharField(max_length=50, label=_('Search'))
	
class SearchForm(forms.Form):
	c = TreeNodeChoiceField(queryset=Category.tree.filter(is_active=True), required=False, label=_('Category'),empty_label=_("the category isn't chosen..."))
	p = forms.ModelChoiceField(queryset=Printer.objects.filter(is_active=True), required=False, label=_('Printer'),empty_label=_("the printer isn't chosen..."))
	q = forms.CharField(max_length=50, required=False, label=_('Search'))
	
	def __init__(self, cat = None, *args, **kwargs):
		super(SearchForm, self).__init__(*args, **kwargs)
		if cat:
			try: self.fields['p'].queryset = Printer.objects.filter(product_printer__category__id=cat, is_active=True).distinct()
			except: pass
			
##################################################################################################	
##################################################################################################

class BasketForm(forms.ModelForm):
	class Meta:
		model = OrderProduct
		fields = ('product', 'count_user')
		widgets = {
			'product':forms.HiddenInput(),
		}
		
	def clean_count(self):
		count_user = self.cleaned_data['count_user']
		if count_user < 1 or count_user > 100000: raise forms.ValidationError(_('Error count_user field'))
		return count_user
		
##################################################################################################	
##################################################################################################

class OrderForm(forms.ModelForm):
	# captcha = CaptchaField()
	agreement = forms.BooleanField(label=_('Agreement'))
	
	def __init__(self, *args, **kwargs):
		super(OrderForm, self).__init__(*args, **kwargs)
		self.fields['name'].required = True
		self.fields['email'].required = True
		self.fields['phone'].required = True
	
	class Meta:
		model = Order
		fields = ('name', 'email', 'phone', 'mbphone', 'address', 'text', 'is_org', 'inn')
		widgets = {'text':forms.Textarea()}
		
	def clean_phone(self): 
		phone = self.cleaned_data['phone']
		r = re.compile('^((\+)?)(\d{1,3})([\- ]?)(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,11}$')
		if not r.findall(phone):
			raise forms.ValidationError(_("Invalid phone field"))
		return phone
		
	def clean_mbphone(self): 
		mbphone = self.cleaned_data['mbphone']
		if mbphone:
			r = re.compile('^((\+)?)(\d{1,3})([\- ]?)(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,11}$')
			if not r.findall(mbphone):
				raise forms.ValidationError(_("Invalid mbphone field"))
			mbphone = re.sub(r'\D', '', mbphone)
		return mbphone
	
	def clean_name(self):
		name = self.cleaned_data['name']
		if len(name) < 3:
			raise forms.ValidationError(_("Invalid name field"))
		return name
		
	def clean_email(self):
		email = self.cleaned_data['email']
		if email:
			r = re.search(r'^[0-9a-zA-Z]([\.-]?\w+)*@[0-9a-zA-Z]([\.-]?[0-9a-zA-Z])*(\.[0-9a-zA-Z]{2,4})+$', email)
			if not r: raise forms.ValidationError(_('Error e-mail field'))
		return email
		
##################################################################################################	
##################################################################################################