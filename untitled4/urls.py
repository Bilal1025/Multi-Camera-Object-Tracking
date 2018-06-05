"""untitled4 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from untitled4.views.views import index, logoff, register, addCamera, getframe, openvideo, closevideo, inittracker, \
    stoptracker, camerabyname, videosview, addVideos, videosbyname, deleteobject

urlpatterns = [
    url(r'^$', index, name='home'),
    url(r'^logout/$', logoff, name='logout'),
    url(r'^register/$', register, name='register'),
    url(r'^videoview/$', videosview, name='videosview'),
    url(r'^addcamera/$', addCamera, name='addcamera'),
    url(r'^addvideos/$', addVideos, name='addvideos'),
    url(r'^deleteobject/$', deleteobject, name='deleteobject'),
    url(r'^camerabyname/$', camerabyname, name='camerabyname'),
    url(r'^videosbyname/$', videosbyname, name='videosbyname'),
    url(r'^getframe/$', getframe, name='getframe'),
    url(r'^openvideo/$', openvideo, name='openvideo'),
    url(r'^closevideo/$', closevideo, name='closevideo'),
    url(r'^inittracker/$', inittracker, name='inittracker'),
    url(r'^stoptracker/$', stoptracker, name='stoptracker'),
]
