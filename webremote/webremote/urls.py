from django.conf.urls import patterns, include, url
from django.template import Context, loader

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'remote.views.index', name='index'),
    # url(r'^webremote/', include('webremote.foo.urls')),

    url(r'^list/$', 'remote.views.list', name='list'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
