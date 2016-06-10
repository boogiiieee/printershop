#coding: utf-8

from django.conf import settings

PARAMS = getattr(settings, 'SMS_PARAMS', {})
URL_SEND = getattr(settings, 'SMS_URL_SEND', '')

RECIPIENT_KEY = getattr(settings, 'SMS_RECIPIENT_KEY', 'to')
MESSAGE_KEY = getattr(settings, 'SMS_MESSAGE_KEY', 'send')