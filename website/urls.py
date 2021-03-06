from django.urls import path
from . import views
from .logic import on_start

on_start()

urlpatterns = [
    path('content/<int:int_index>/', views.lot_content, name='lot_content'),
    path('hdd_delete_order/<int:int_index>/', views.hdd_delete_order, name='hdd_delete_order'),
    path('hdd_order_content/<int:int_index>/', views.hdd_order_content, name='hdd_order_content'),
    path('hdd_edit/<int:int_index>/', views.hdd_edit, name='hdd_edit'),
    path('hdd_delete/<int:int_index>/', views.hdd_delete, name='hdd_delete'),
    path('view_pdf/<int:int_index>/', views.view_pdf, name='view_pdf'),
    path('log/', views.log, name='log'),
    path('pdf/', views.pdf, name='pdf'),
    path('tar/', views.tar, name='tar'),
    path('new_hdd_order/', views.hdd_order, name='new_hdd_order'),
    path('', views.index, name='index'),
]