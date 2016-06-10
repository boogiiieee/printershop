# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.conf import settings
from django.core.mail import EmailMessage

import threading

################################################################################################################
################################################################################################################

def letter_send_mail(template, head, addresses, params):
	body = '%s' % render_to_response(template, params)._get_content()
	msg = EmailMessage(head, body, settings.DEFAULT_FROM_EMAIL, addresses)
	msg.content_subtype = "html"
	t = threading.Thread(target=msg.send)
	t.start()

################################################################################################################
################################################################################################################