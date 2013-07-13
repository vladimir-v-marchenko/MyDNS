from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('web2dns.views',
	url(r'^$', lambda x: HttpResponseRedirect('/accounts/profile/')),
	url(r'^ip/', 'ip', name='show-ip'),

	url(r'^update/$', 'update', name='update'),
	#url(r'update/(?P<rrname>[a-zA-Z0-9\.-]+)/(?P<content>[0-9\.]{7,15})/', 'simple_update', name='simple_update'),

	url(r'^accounts/profile/', 'profile', name='profile'),

)

urlpatterns += patterns('',
	url(r'^accounts/', include('django.contrib.auth.urls')),
)



