# Create your views here.
from django.shortcuts import render
from integrations.models import Integration
from django.shortcuts import redirect
from integrations import authentication as auth
from datetime import datetime, timezone, timedelta
import urllib.parse
from django.apps import apps as proj_apps
import environ
import json

env = environ.Env()
environ.Env.read_env()


def index(request):
    context = {
        "title": "Connectors",
        "list": proj_apps.get_app_config('integrations').integration_config.keys()
    }
    return render(request, "integration.html", context)


def authorization(request, app):
    integration_config = proj_apps.get_app_config('integrations').integration_config[app]
    instance_id = app
    if request.method == 'POST':
        if integration_config['auth_method'] == 'OAUTH2':
            authorization_params = integration_config['authorization_params']
            response_type = authorization_params.get('response_type', '')
            if authorization_params.get('auth_callback', False):
                redirect_uri = env.str('DOMAIN',
                                       default='http://localhost:8000/') + 'integrations/oauth-callback/' + app
            client_id = request.POST['client_id']
            client_secret = request.POST['client_secret']
            url_dict = {'client_id': client_id}
            if redirect_uri:
                url_dict['redirect_uri'] = redirect_uri
            if response_type:
                url_dict['response_type'] = response_type
            scopes = []
            scope_str = None
            if 'scope_params' in integration_config:
                scope_params = integration_config['scope_params']
                scope_separator = scope_params.get('scope_separator', ' ')
                if 'default_scopes' in scope_params:
                    scopes = [s.strip() for s in scope_params['default_scopes'].split(scope_separator)]
                for scope in request.POST.getlist('object_scopes'):
                    scope_item = [s.strip() for s in scope.split(scope_separator)]
                    scopes += scope_item

                scope_str = scope_separator.join(scopes)
            if len(scopes) > 0 and scope_params['request_type'] == 'request_param':
                url_dict['scope'] = scope_str

            try:
                integration = Integration.objects.get(name=app, instance_id=instance_id)
                integration.client_id = client_id
                integration.client_secret = client_secret
                integration.scope = scope_str
                integration.redirect_uri = redirect_uri
                integration.instance_id = instance_id
                integration.save()

            except Integration.DoesNotExist:
                integration = Integration(name=app,
                                          client_id=client_id,
                                          client_secret=client_secret,
                                          scope=scope_str,
                                          redirect_uri=redirect_uri,
                                          instance_id=instance_id)
                integration.save()

            url_encoding = urllib.parse.urlencode(url_dict)
            return redirect(integration_config['authorization_url'] + "?" + url_encoding)

        if integration_config['auth_method'] == 'APIKEY':
            api_key = request.POST['api_key']
            try:
                integration = Integration.objects.get(name=app, instance_id=instance_id)
                integration.api_key = api_key
                integration.enabled = True
                integration.instance_id = instance_id
                integration.save()
            except Integration.DoesNotExist:
                integration = Integration(name=app,
                                          api_key=api_key, enabled=True, instance_id=instance_id)

                integration.save()

    return redirect('/')


def oauth_callback(request):
    parts = [s.strip() for s in request.path.split('/')]
    app = parts[len(parts) - 1]
    instance_id = app
    integration_config = proj_apps.get_app_config('integrations').integration_config[app]
    authorization_params = integration_config['authorization_params']
    token_params = integration_config['token_params']
    authorization_code = request.GET.get(authorization_params['response_type'], '')

    try:
        integration = Integration.objects.get(instance_id=instance_id)
        integration.authorization_code = authorization_code
        integration.save()

        token_request = auth.TokenRequest()
        token_request.client_id = integration.client_id
        token_request.authorization_code = authorization_code
        token_request.client_secret = integration.client_secret
        token_request.redirect_uri = integration.redirect_uri
        token_result = auth.request_token_with_code(integration_config['token_url'], token_params['grant_type'],
                                                    token_request)

        if token_result.success:

            integration.auth_json = json.dumps(token_result.json_body)
            integration.access_token = token_result.access_token
            integration.refresh_token = token_result.refresh_token
            if token_result.expires_in:
                integration.expire_at = datetime.now(timezone.utc) + timedelta(
                    seconds=token_result.expires_in)
            elif token_params.get('expire_in', None):
                integration.expire_at = datetime.now(timezone.utc) + timedelta(
                    seconds=int(token_params['expire_in']))

            integration.enabled = True
            integration.save()

        else:
            context = {
                "title": "Authentication Error",
                "status_code": token_result.status_code,
                "error": token_result.json_body
            }
            return render(request, "error.html", context)

    except Integration.DoesNotExist:
        context = {
            "title": "Authentication Error",
            "status_code": "",
            "error": "Please try connect " + app + " again."
        }
        return render(request, "error.html", context)

    return redirect('/')


def connect(request, app):
    context = {
        "title": "Connect " + app,
        "config": proj_apps.get_app_config('integrations').integration_config[app]
    }
    # return response with template and context
    return render(request, 'connectors/' + app + ".html", context)
