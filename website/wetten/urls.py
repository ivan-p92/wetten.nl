from django.conf.urls import patterns, url

from wetten import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^doc/(?P<document>.*)$', views.doc, name='doc'),
)
