from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^admin/filebrowser/', include('filebrowser.urls')),
	url(r'^tinymce/', include('tinymce.urls')),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^admin_tools/', include('admin_tools.urls')),
	url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
	url(r'^captcha/', include('captcha.urls')),
	url(r'^rosetta/', include('rosetta.urls')),
	#url(r'^i18n/', include('django.conf.urls.i18n')),
	
	url(r'^', include('project.urls')),
	url(r'^', include('shop.urls')),

	url(r'^pay/', include('pay.urls')),
	url(r'^configuration/', include('configuration.urls')),
)