from django.urls import path, re_path
from . import views

urlpatterns = [
    path("connectors", views.connector, name="connectors"),
    path("config/<str:app>", views.app_config, name="app_config")
]