from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("connect/<str:app>", views.connect, name="connect"),
    path("connectors", views.connector, name="connectors"),
    path("authorize/<str:app>", views.authorization, name="authorization"),
    re_path(r"oauth-callback?[-a-zA-Z0-9%._+~#=]+", views.oauth_callback, name="oauth_callback"),
]