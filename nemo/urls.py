from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required, permission_required

import nemo.views as nv
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    #url(r'^$', nv.IndexV.as_view()),
    url(r'^(?P<stream_type>hot|top|all|done)?/?$', nv.IndexV.as_view()),
    url(r'^create/$', login_required(nv.CreateV.as_view())),
    url(r'^update/(?P<pk>\d+)/$', login_required(nv.UpdateV.as_view())),
    url(r'^response/(?P<pk>\d+)/$', 
        permission_required('wishlist.response_wish')(nv.ResponseV.as_view())),
    url(r'^list/(?P<stream_type>hot|top|all|done)/(since)?(?P<since>\d+)?/?(till)?(?P<till>\d+)?/?$', nv.ListV.as_view()),
    url(r'^vote/(?P<pk>\d+)/$', login_required(nv.VoteV.as_view()))
)
