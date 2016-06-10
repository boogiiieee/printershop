from django.conf.urls.defaults import *

urlpatterns = patterns('configuration.views',
	(r'form/save/$','save_config'),
)