from django.conf.urls import url

from . import views

app_name = 'gendep'

# Some info about url patterns: http://www.webforefront.com/django/accessurlparamsviewmethods.html
# Optional parameters: http://stackoverflow.com/questions/14351048/django-optional-url-parameters

urlpatterns = [
    url(r'^$', views.index, name='home'),
    
    url(r'^about/$', views.about, name='about'),
    url(r'^drivers/$', views.drivers, name='drivers'),
    url(r'^targets/$', views.targets, name='targets'),
    url(r'^tissues/$', views.tissues, name='tissues'),
    url(r'^studies/$', views.studies, name='studies'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^faq/$', views.faq, name='faq'),
    
    # url(r'^(?P<driver>[0-9A-Z]+)/graph/$', views.graph, name='graph'),

    url(r'^study/(?P<study_pmid>[0-9A-Za-z]+)/$', views.show_study, name='show_study'), # pmid could be 'Pending0001'

    url(r'^get_drivers/', views.get_drivers, name='get_drivers'),    
    
    url(r'^get_dependencies/(?P<search_by>(?:mysearchby|driver|target))/(?P<gene_name>[0-9A-Za-z\-_\.]+)/(?P<histotype_name>[0-9A-Za-z\_]+)/(?P<study_pmid>[0-9A-Za-z\_]+)/$', views.ajax_results_fast_minimal_data_version, name='get_dependencies'), 
    # '\_' is needed to match ALL_STUDIES and ALL_HISTOTYPES

    url(r'^ajax_results/', views.ajax_results_slow_full_detail_version, name='ajax_results_post'),
    
    url(r'^download_csv/(?P<search_by>(?:mysearchby|driver|target))/(?P<gene_name>[0-9A-Za-z\-_\.]+)/(?P<histotype_name>[0-9A-Za-z\_]+)/(?P<study_pmid>[0-9A-Za-z\_]+)/$', views.download_dependencies_as_csv_file, name='download_csv'), # \_ needed to match ALL_STUDIES and ALL_HISTOTYPES
    
    url(r'^get_gene_info/(?P<gene_name>[0-9A-Za-z\-_\.]+)/$', views.gene_info, name='get_gene_info'), # tip=element.data('url'),
    
    url(r'^qtip/(?P<query>[0-9A-Za-z\-_\.]+)/$', views.qtip, name='qtip'), # tip=element.data('url'),

    # url(r'^driver/(?P<driver>[0-9A-Za-z\-_\.]+)/$', views.index, name='driver'), # ie: /driver/gene_name/    
    url(r'^(?P<search_by>driver|target)/(?P<gene_name>[0-9A-Za-z\-_\.]+)/$', views.index, name='home_search_by'), # Needs to be at end as could otherwise interpret 'about' as driver name.

]
