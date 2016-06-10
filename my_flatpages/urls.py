from django.conf.urls.defaults import *

urlpatterns = patterns('my_flatpages.views',
    (r'^(?P<url>.*)$', 'flatpage'),
)
