from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('blog.urls')),
    (r'^api/', include('api.urls')),
    (r'^admin/', include(admin.site.urls)),
)
