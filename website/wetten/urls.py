from django.conf.urls import patterns, url

from wetten import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^doc/(?P<document>.*)$', views.doc, name='doc'),
    url(r'^related/$', views.related, name='related'),
    url(r'^relatedContent/$', views.relatedContent, name='relatedContent'),
    url(r'^reference/$', views.reference, name='reference'),
    url(r'^timetravelArticle/$', views.timetravelArticle, name='timetravelArticle'),
    url(r'^metalexContent/$', views.metalexContent, name='metalexContent'),
    url(r'^timetravelParagraph/$', views.timetravelParagraph, name='timetravelParagraph'),
    url(r'^bwb/$', views.bwb, name='bwb'),
    url(r'^help/$', views.handleiding, name='handleiding')
)
