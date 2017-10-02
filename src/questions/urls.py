from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^all/$', views.all, name='all'),
    url(r'^topics/$', views.topics, name='topics'),

    url(r'^respond/$', views.respond, name='respond'),
    url(r'^rate/$', views.rate, name='rate'),

    url(r'^id/(.*)/$', views.id),
    url(r'^page/(.*)/$', views.page),
    url(r'^competencies/all/$', views.competencies),
    url(r'^search/$', views.search)
]
