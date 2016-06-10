#coding: utf-8

import urllib
import urllib2
import threading

from sms.models import SmsModel
from sms.conf import settings

################################################################################################################
################################################################################################################

class Sms():
	def __init__(self, message = u'', recipient = []):
		self.message = message.encode('utf-8')
		self.recipients = []
		for i in recipient:
			self.recipients.append(i.encode('utf-8'))
		
	def send(self):
		for recipient in self.recipients:
			params = {
				settings.RECIPIENT_KEY:recipient,
				settings.MESSAGE_KEY:self.message,
			}
			params.update(settings.PARAMS)
			
			s = SmsModel.objects.create(to = recipient, text = self.message, status = '0')
			req = urllib2.Request(settings.URL_SEND, urllib.urlencode(params))
			
			try: page = urllib2.urlopen(req).read()
			except:
				s.status = '2'
				s.save()
			else:
				s.status = '1'
				s.save()
		return True
		
	def thread_send(self): 
		t = threading.Thread(target=self.send()) 
		t.start()
		
################################################################################################################
################################################################################################################