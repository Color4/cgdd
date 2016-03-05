from django.conf.urls import url

from . import views

app_name = 'gendep'
urlpatterns = [
    url(r'^$', views.index, name='home'),
    
    url(r'^about/$', views.about, name='about'),
    url(r'^drivers/$', views.drivers, name='drivers'),
    url(r'^studies/$', views.studies, name='studies'),
    url(r'^contact/$', views.contact, name='contact'),

    # url(r'^driver/(?P<driver>[0-9A-Za-z]+)/$', views.index, name='driver'), # ie: /driver/driver_name/
    url(r'^driver/(?P<driver>[0-9A-Za-z\-_\.]+)/$', views.index, name='driver'), # ie: /driver/driver_name/
    
    url(r'^(?P<driver>[0-9A-Z]+)/graph/$', views.graph, name='graph'),
	url(r'^results/$', views.results, name='results'),
    url(r'^study/(?P<pmid>[0-9A-Za-z]+)/$', views.show_study, name='show_study'),

    url(r'^get_drivers/', views.get_drivers, name='get_drivers'),
    url(r'^ajax_results/', views.ajax_results, name='ajax_results'),
    
    url(r'^(?P<driver>[0-9A-Za-z\-_\.]+)/$', views.index, name='home_driver'), # Needs to be at end as could otherwise interpret 'about' as driver name. 
]
