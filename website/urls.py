from django.urls import path
from . import views
from .logic import on_start

on_start()

urlpatterns = [
    path('log/', views.log, name='log'),
    path('pdf/', views.pdf, name='pdf'),
    # path('tar/', views.tar, name='tar'),
]