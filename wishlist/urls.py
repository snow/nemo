from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required, permission_required

from wishlist.views import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', IndexV.as_view()),
    url(r'^create/$', login_required(CreateV.as_view())),
    url(r'^update/(?P<pk>\d+)/$', login_required(UpdateV.as_view())),
    url(r'^response/(?P<pk>\d+)/$', 
        permission_required('wishlist.response')(ResponseV.as_view())),
    url(r'^list/$', ListV.as_view()),
    url(r'^vote/(?P<pk>\d+)/$', login_required(VoteV.as_view()))
)
