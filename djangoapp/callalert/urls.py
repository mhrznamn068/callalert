from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('call/', views.call, name='call'),
    path('zabbix/', views.zabbix, name='zabbix'),
    path('prometheus/', views.prometheus, name='prometheus')
]