СМС рассылка

1) 'sms', в settings
2)	SMS_PARAMS = {}, SMS_URL_SEND = 'http://domain.ru/path/' в settings
3)  sms = Sms('text sms', ['phone1', 'phone2']).send() / .thread_send()