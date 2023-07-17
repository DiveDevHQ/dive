import dive.api.request_utils as ru
from integrations.models import Integration
from datetime import datetime, timezone, timedelta
from django.apps import apps as proj_apps
import json


class TokenRequest:
    client_id = ""
    client_secret = ""
    redirect_uri = ""
    refresh_token = ""
    access_token = ""
    authorization_code = ""
    json_body = ""
    token_type = ""


class TokenResult:
    access_token = ""
    refresh_token = ""
    expires_in = None
    success = False
    json_body = None
    status_code = None


def get_config(app):
    return proj_apps.get_app_config('integrations').integration_config.get(app, None)


def get_auth(connector_id):
    try:
        integration = Integration.objects.get(connector_id=connector_id, enabled=True)
        integration_config = proj_apps.get_app_config('integrations').integration_config.get(integration.name, None)
        if not integration_config:
            return None, None
        if integration_config['auth_method'] == 'APIKEY':
            return integration, integration.api_key
        elif integration_config['auth_method'] == 'NOAUTH':
            return integration, None
        elif integration_config['auth_method'] == 'OAUTH2':
            if not integration.expire_at:
                return integration, integration.access_token
            elif integration.expire_at and datetime.now(timezone.utc) + timedelta(
                    seconds=120) < integration.expire_at:
                return integration, integration.access_token
            else:
                token_request = TokenRequest()
                token_request.client_id = integration.client_id
                token_request.redirect_uri = integration.redirect_uri
                token_request.client_secret = integration.client_secret
                token_request.refresh_token = integration.refresh_token
                token_result = refresh_token(integration_config['token_url'],
                                             integration_config['refresh_params']['grant_type'], token_request)
                if token_result.success:
                    integration.access_token = token_result.access_token
                    if token_result.refresh_token:
                        integration.refresh_token = token_result.refresh_token
                    if token_result.expires_in:
                        integration.expire_at = datetime.now(timezone.utc) + timedelta(
                            seconds=token_result.expires_in)
                    integration.save()
                    return integration, integration.access_token
                else:
                    return None, None

    except Integration.DoesNotExist:
        return None, None
    return None, None


def refresh_token(url, grant_type, token_request: TokenRequest):
    form_data = {'grant_type': grant_type}
    if token_request.refresh_token:
        form_data['refresh_token'] = token_request.refresh_token
    if token_request.client_id:
        form_data['client_id'] = token_request.client_id
    if token_request.redirect_uri:
        form_data['redirect_uri'] = token_request.redirect_uri
    if token_request.client_secret:
        form_data['client_secret'] = token_request.client_secret

    response = ru.post_request_with_form(url, form_data)
    token_result = TokenResult()
    token_result.success = response.success
    token_result.json_body = response.json_body
    token_result.status_code = response.status_code
    if response.success:
        token_result.access_token = response.json_body['access_token']
        if 'refresh_token' in response.json_body:
            token_result.refresh_token = response.json_body['refresh_token']
        if 'expires_in' in response.json_body:
            token_result.expires_in = response.json_body['expires_in']

    return token_result


def request_token_with_code(url, grant_type, token_request: TokenRequest):
    form_data = {'grant_type': grant_type}
    if token_request.client_id:
        form_data['client_id'] = token_request.client_id
    if token_request.redirect_uri:
        form_data['redirect_uri'] = token_request.redirect_uri
    if token_request.client_secret:
        form_data['client_secret'] = token_request.client_secret
    if token_request.authorization_code:
        form_data['code'] = token_request.authorization_code

    response = ru.post_request_with_form(url, form_data)

    token_result = TokenResult()
    token_result.success = response.success
    token_result.json_body = response.json_body
    token_result.status_code = response.status_code
    if response.success:
        token_result.access_token = response.json_body['access_token']
        token_result.refresh_token = response.json_body['refresh_token']
        if 'expires_in' in response.json_body:
            token_result.expires_in = response.json_body['expires_in']
    return token_result


def get_last_sync_at(connector_id, obj_type):
    try:
        integration = Integration.objects.get(connector_id=connector_id, enabled=True)
        if integration.sync_status:
            sync_status = json.loads(integration.sync_status)
            if 'obj_status' in sync_status and obj_type in sync_status['obj_status']:
                return sync_status['obj_status'][obj_type].get('sync_at',None)
    except Integration.DoesNotExist:
        return
    return


def update_last_sync(connector_id, obj_type):
    try:
        integration = Integration.objects.get(connector_id=connector_id, enabled=True)
        sync_status = {'obj_status': {}}
        if integration.sync_status:
            sync_status = json.loads(integration.sync_status)
            if 'error' in integration.sync_status:
                del sync_status['error']
            if 'obj_status' not in integration.sync_status:
                sync_status['obj_status'] = {}

        if obj_type in sync_status['obj_status']:
            sync_status['obj_status'][obj_type] = {'sync_at': get_now_iso_format()}
        else:
            sync_status['obj_status'][obj_type] = {'sync_at': get_now_iso_format()}
        integration.sync_status = json.dumps(sync_status)
        integration.save()
    except Integration.DoesNotExist:
        return


def update_sync_error(connector_id, error):
    try:
        integration = Integration.objects.get(connector_id=connector_id, enabled=True)
        sync_status = {'error': {}}
        if integration.sync_status:
            sync_status = json.loads(integration.sync_status)
        sync_status['error'] = error
        integration.sync_status = json.dumps(sync_status)
        integration.save()
    except Integration.DoesNotExist:
        return


def clear_sync_status(connector_id):
    try:
        integration = Integration.objects.get(connector_id=connector_id, enabled=True)
        integration.sync_status = None
        integration.save()
    except Integration.DoesNotExist:
        return


def get_now_iso_format():
    now = datetime.now()
    iso_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return iso_time
