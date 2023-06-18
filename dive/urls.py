"""
URL configuration for dive project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import include,path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("api/authorize/<str:app>", views.authorization_api, name="authorization_api"),
    path("api/callback", views.callback_api, name="callback_api"),
    path("api/crm/v1/<str:obj_type>/<str:obj_id>", views.get_or_patch_crm_data_by_id, name="get_or_patch_crm_data_by_id"),
    path("api/crm/v1/<str:obj_type>", views.get_or_create_crm_data, name="get_or_create_crm_data"),
    path("api/crm/v1/<str:obj_type>/meta/field-properties", views.get_crm_field_properties, name="get_crm_field_properties"),
    path("api/crm/v1/<str:obj_type>/data/index", views.index_crm_data, name="index_crm_data"),
    path("api/v1/documents/search", views.get_index_data, name="get_index_data"),
    path("integrations/", include("integrations.urls")),
    path('admin/', admin.site.urls),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
