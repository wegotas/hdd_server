from django.urls import path
from . import views
from .logic import on_start

on_start()

urlpatterns = [
    path('content/<int:int_index>/', views.lot_content, name='lot_content'),
    path('hdd_edit/<int:int_index>/', views.hdd_edit, name='hdd_edit'),
    path('log/', views.log, name='log'),
    path('pdf/', views.pdf, name='pdf'),
    path('tar/', views.tar, name='tar'),
    path('', views.index, name='index'),
]