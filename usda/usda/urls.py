from django.contrib import admin
from scrape import views
from django.conf import settings
from django.conf.urls import patterns, include, url

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.LicenseeCertListView.as_view(), name='licenseecert-list'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
