"""Poker URL Configuration

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
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from PokerApp import views
from django.conf.urls.static import static
from Poker import settings

urlpatterns = [
    url(r'^$', views.main, name='index'),
    url(r'^register/$', views.RegisterFormView.as_view()),
    url(r'^logout/$', views.LogoutView.as_view()),
    url(r'^login/$', views.LoginFormView.as_view()),
    url(r'^profile/(\w+)/$', views.profile),
    url(r'^lobby/(\w+)/$', views.LobbyView.as_view()),
    url(r'^lobby/(\w+)/game/call/$', views.call),
    url(r'^lobby/(\w+)/game/call/flop/$', views.call),
    url(r'^lobby/(\w+)/game/call/turn/$', views.call),
    url(r'^lobby/(\w+)/game/call/river/$', views.call),
    url(r'^lobby/(\w+)/game/check/$', views.check),
    url(r'^lobby/(\w+)/game/check/flop/$', views.check),
    url(r'^lobby/(\w+)/game/check/turn/$', views.check),
    url(r'^lobby/(\w+)/game/check/river/$', views.check),
    url(r'^lobby/(\w+)/game/fold/$', views.fold),
    url(r'^lobby/(\w+)/game/fold/flop/$', views.fold),
    url(r'^lobby/(\w+)/game/fold/turn/$', views.fold),
    url(r'^lobby/(\w+)/game/fold/river/$', views.fold),
    url(r'^lobby/(\w+)/game/$', views.StartGame.as_view(), name='game'),
    url(r'^lobby/(\w+)/game/flop/$', views.FlopRound.as_view(), name='flop'),
    url(r'^lobby/(\w+)/game/turn/$', views.TurnRound.as_view(), name='turn'),
    url(r'^lobby/(\w+)/game/river/$', views.RiverRound.as_view(), name='river'),
    url(r'^lobby/(\w+)/game/showdown/$', views.ShowDown.as_view()),
    url(r'^(?P<pk>\d+)/$', views.UpdateProfile.as_view()),
    url(r'^password/$', views.change_password, name='change_password'),
    path('admin/', admin.site.urls)
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
