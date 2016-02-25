from django.conf.urls import url

from . import views

app_name = 'gendep'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<driver_name>[0-9A-Z]+)/graph/$', views.graph, name='graph'),
	url(r'^results/$', views.results, name='results'),
 #   url(r'^api/get_drivers/', views.get_drivers, name='get_drivers'),
    url(r'^get_drivers/', views.get_drivers, name='get_drivers'),
]
