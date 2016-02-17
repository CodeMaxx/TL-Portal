"""portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from issuestuff.views import *
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'issuestuff.views.my_404_view'
handler500 = 'issuestuff.views.my_404_view'

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_site/([^/]+)',admin_interface,name="admin_interface"),
    url(r'^enter/$', enter, name='enter'),
    url(r'^exit/$', exit, name='exit'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^login/$', login, name='login'),
    url(r'^redirect/$', redirect_function, name='redirect'),
    url(r'^home/$', home, name='home'),
    url(r'^records/$', tl_records, name='records'),
    url(r'^stuff/$', issuestuff, name='issuestuff'),
    url(r'^secondary_email/$', enter_secondary_email, name='secondary_email'),
    # url(r'^TL_records/$', TL_records, name='redirect'),
    url(r'^$', mainpage, name='default'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


