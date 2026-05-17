"""
URL configuration for Goshen Laboratory app.

Usage: include('lab.urls', namespace='lab') in main urls.py
"""
from django.urls import path
from . import views

app_name = 'lab'

urlpatterns = [
    path('', views.index, name='index'),
]
