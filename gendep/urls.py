from django.conf.urls import url

from . import views

app_name = 'gendep'

# Some info about url patterns: http://www.webforefront.com/django/accessurlparamsviewmethods.html
# Optional parameters: http://stackoverflow.com/questions/14351048/django-optional-url-parameters

urlpatterns = [
    url(r'^$', views.index, name='home'),
    
    url(r'^about/$', views.about, name='about'),
    url(r'^drivers/$', views.drivers, name='drivers'),
    url(r'^studies/$', views.studies, name='studies'),
    url(r'^contact/$', views.contact, name='contact'),

    # url(r'^driver/(?P<driver>[0-9A-Za-z]+)/$', views.index, name='driver'), # ie: /driver/driver_name/
    url(r'^driver/(?P<driver>[0-9A-Za-z\-_\.]+)/$', views.index, name='driver'), # ie: /driver/driver_name/
    
    url(r'^(?P<driver>[0-9A-Z]+)/graph/$', views.graph, name='graph'),
	# url(r'^results/$', views.results, name='results'), No longer used
    url(r'^study/(?P<pmid>[0-9A-Za-z]+)/$', views.show_study, name='show_study'), # pmid could be 'Pending0001'

    url(r'^get_drivers/', views.get_drivers, name='get_drivers'),
    url(r'^ajax_results/', views.ajax_results, name='ajax_results'),
    
    url(r'^download_csv/(?P<driver_name>[0-9A-Za-z\-_\.]+)/(?P<histotype_name>[0-9A-Za-z\_]+)/(?P<study_pmid>[0-9A-Za-z\_]+)/$', views.download_dependencies_as_csv_file, name='download_csv'), # \_ needed to match ALL_STUDIES and ALL_HISTOTYPES
    
    url(r'^(?P<driver>[0-9A-Za-z\-_\.]+)/$', views.index, name='home_driver'), # Needs to be at end as could otherwise interpret 'about' as driver name. 
]
