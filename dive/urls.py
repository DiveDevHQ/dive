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
    path("about", views.about, name="about"),
    path("apps/<str:account_id>", views.get_connected_apps, name="get_connected_apps"),
    path("setup/vector", views.initialize_vector, name="initialize_vector"),
    path("sync/<str:app>/<str:account_id>/<str:connector_id>", views.sync_instance_data, name="sync_instance_data"),
    path("clear/<str:app>/<str:account_id>/<str:connector_id>", views.clear_instance_data, name="clear_instance_data"),
    path("api/authorize/<str:app>", views.authorization_api, name="authorization_api"),
    path("api/callback", views.callback_api, name="callback_api"),
    path("api/crm/v1/<str:obj_type>/<str:obj_id>", views.get_or_patch_crm_data_by_id, name="get_or_patch_crm_data_by_id"),
    path("api/crm/v1/<str:obj_type>", views.get_or_create_crm_data, name="get_or_create_crm_data"),
    path("api/crm/v1/<str:obj_type>/meta/field-properties", views.get_crm_field_properties, name="get_crm_field_properties"),
    path("api/v1/documents/search", views.get_query_data, name="get_query_data"),
    path("api/v1/message/queue/<str:user_id>", views.get_or_delete_message_queue, name="get_or_delete_message_queue"),
    path("api/v1/message/add", views.add_message, name="add_message"),
    path("api/v1/message/incoming/<str:user_id>", views.get_message, name="get_message"),
    path("schemas/<str:app>/<str:module>", views.get_obj_schemas, name="get_schemas"),
    path("templates/<str:app>/<str:module>/<str:account_id>", views.get_obj_templates, name="get_templates"),
    path("template/<str:template_id>", views.patch_or_delete_template, name="patch_or_delete_template"),
    path("template", views.add_obj_template, name="add_template"),
    path("integrations/", include("integrations.urls")),
    path('admin/', admin.site.urls),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

