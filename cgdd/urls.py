"""gcdd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
#    url(r'^(?:gendep|api)/', include('gendep.urls')), # This didn't work, (as genedp.utls contains app_name = 'gendep') but split the gendep urls in two files, but keep as one for simplicity for now.
    url(r'^admin/', admin.site.urls),
    url(r'^gendep/', include('gendep.urls')),
#    url(r'^api/', include('gendep.urls_api')),
    
    # To enable the domain name: "http://www.cancergd.org" to go to the gendep app, without needing /gendep/ suffix.
    # From: http://stackoverflow.com/questions/22468813/how-do-i-set-my-django-views-url-to-the-root-domain-of-my-website    
    # The following url should be the final url() here so that Django can test for matches to the above urls first.
    url(r'^', include('gendep.urls', namespace = "gendep")),    
]
