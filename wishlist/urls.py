from django.conf.urls.defaults import patterns, include, url

from wishlist.views import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', IndexV.as_view()),
    url(r'^create/$', CreateV.as_view()),
    url(r'^list/$', ListV.as_view()),
    url(r'^vote/(?P<pk>\d+)/$', VoteV.as_view())
)
