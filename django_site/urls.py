from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', 
        {'next_page': '/'}),

    url(r'^admin/', include(admin.site.urls)),
    url(settings.NEMO_URI_ROOT[1:], include('nemo.urls')),
    
    url('^$', RedirectView.as_view(url=settings.NEMO_URI_ROOT,
                                   query_string=True,
                                   permanent=False))
)
