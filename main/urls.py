from django.conf.urls import patterns, url
from main import views

urlpatterns = patterns('',
    url(r'^submitRequest', views.submitRequest, name='submitRequest'),
    url(r'^response', views.response, name='response'),
    url(r'^submitResponse', views.submitResponse, name='submitResponse'),
    url(r'^refresh', views.refresh, name='refresh'),
    )
