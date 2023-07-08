# Create your views here.
from django.shortcuts import render
from integrations.models import Integration
from django.shortcuts import redirect

from django.apps import apps as proj_apps
from rest_framework.decorators import action, api_view
from django.http import JsonResponse
import environ

env = environ.Env()
environ.Env.read_env()


@api_view(["GET"])
def connector(request):
    apps = proj_apps.get_app_config('integrations').integration_config.keys()
    results = []
    for app in apps:
        config = proj_apps.get_app_config('integrations').integration_config[app]
        modules = []
        for m in config['module']:
            modules.append(m['schema'])
        results.append({'name': app, 'modules': modules})
    return JsonResponse(results, safe=False)


@api_view(["GET"])
def app_config(request, app):
    config = proj_apps.get_app_config('integrations').integration_config[app]
    return JsonResponse(config, safe=False)
