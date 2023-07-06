from integrations.models import Integration
from integrations.models import Template
from integrations import authentication as auth
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse
from datetime import datetime, timezone, timedelta
from dive.api.exceptions import UnauthorizedException
import importlib
from dive.api.exceptions import BadRequestException
from urllib.parse import parse_qs, urlencode
from rest_framework.decorators import action, api_view
from django.http import HttpResponse
import json
import environ
import copy
from dive.api.utils import get_params
from time import sleep
from dive.api import vector_utils

env = environ.Env()
environ.Env.read_env()


# schema_view = get_swagger_view(title='Dive API')

def index(request):
    return redirect(env.str('HOME_URL',default='http://localhost:3000'))


def get_connected_apps(request):
    integrations = Integration.objects.filter(enabled=True)
    connectors = []
    for i in integrations:
        connectors.append({'instance_id': i.instance_id, 'app': i.name, 'sync_status':i.sync_status})
    return JsonResponse(connectors, safe=False)


def sync_config(request, schema):
    templates = Template.objects.filter(schema=schema, deleted=False)
    template_list = []
    for template in templates:
        template_list.append({'id': template.id, 'obj_type': template.obj_type, 'content': template.content})

    context = {
        "title": schema + " template",
        "api": schema,
        "list": template_list
    }
    return render(request, "sync.html", context)


def sync_data(request, schema):
    if request.method == 'POST':
        obj_type = request.POST['obj_type']
        template_text = request.POST['template']
        template_id = request.POST['template_id']
        if template_id and not obj_type and not template_text:
            try:
                template = Template.objects.get(id=template_id)
                template.deleted = True
                template.save()
            except Template.DoesNotExist:
                return redirect('/')
            return redirect('/')
        elif obj_type and template_text:
            try:
                template = Template.objects.get(schema=schema, obj_type=obj_type)
                template.content = template_text
                template.deleted = False
                template.save()
            except Template.DoesNotExist:
                template = Template(schema=schema,
                                    obj_type=obj_type,
                                    content=template_text)
                template.save()

            integrations = Integration.objects.filter(enabled=True)
            for i in integrations:
                config = auth.get_config(i.name)
                if not config:
                    continue
                for a in config['api']:
                    if a['schema'] == schema:
                        index_data_reset(schema, i.instance_id, obj_type, template_text)

    return redirect('/')


@api_view(["POST"])
def authorization_api(request, app):
    integration_config = auth.get_config(app)
    if not integration_config:
        raise BadRequestException('provider ' + app + ' is not supported')
    instance_id = request.data.get('instance_id', '')
    if not instance_id:
        raise BadRequestException('instance_id is required')
    redirect_uri = request.data.get('redirect_uri', '')
    if not redirect_uri:
        raise BadRequestException('redirect_uri is required')
    if integration_config['auth_method'] == 'OAUTH2':
        authorization_params = integration_config['authorization_params']
        response_type = authorization_params.get('response_type', '')
        client_id = request.data.get('client_id', '')
        client_secret = request.data.get('client_secret', '')
        object_scopes = request.data.get('object_scopes', '')
        if not client_id or not client_secret:
            raise BadRequestException('client_id, client_secret are required')
        url_dict = {'client_id': client_id}
        if authorization_params.get('auth_callback', False) and redirect_uri:
            url_dict['redirect_uri'] = redirect_uri
        if response_type:
            url_dict['response_type'] = response_type
        scopes = []
        scope_str = None
        if 'scope_params' in integration_config:
            scope_params = integration_config['scope_params']
            scope_separator = scope_params.get('scope_separator', ', ')
            if 'default_scopes' in scope_params:
                scopes = [s.strip() for s in scope_params['default_scopes'].split(scope_separator)]
            scope_item = [s.strip() for s in object_scopes.split(scope_separator)]
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

        url_encoding = urlencode(url_dict)
        return JsonResponse({'redirect': integration_config['authorization_url'] + "?" + url_encoding})

    if integration_config['auth_method'] == 'APIKEY':
        api_key = request.data.get('api_key', '')
        if not api_key:
            raise BadRequestException('api_key is required')
        try:
            integration = Integration.objects.get(name=app, instance_id=instance_id)
            integration.api_key = api_key
            integration.enabled = True
            integration.instance_id = instance_id
            integration.redirect_uri = redirect_uri
            integration.save()
        except Integration.DoesNotExist:
            integration = Integration(name=app,
                                      api_key=api_key, enabled=True, instance_id=instance_id,
                                      redirect_uri=redirect_uri)

            integration.save()
        return JsonResponse({'redirect': redirect_uri})


@api_view(["POST"])
def callback_api(request):
    authorization_code = request.data.get('code', '')
    instance_id = request.data.get('instance_id', '')
    if not authorization_code:
        raise BadRequestException("code is required")
    if not instance_id:
        raise BadRequestException("instance_id is required")
    try:
        integration = Integration.objects.get(instance_id=instance_id)
        integration_config = auth.get_config(integration.name)
        if not integration_config:
            raise BadRequestException('provider ' + integration.name + ' is not supported')
        token_params = integration_config['token_params']
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
            print(token_result.json_body)
            raise BadRequestException(token_result.json_body)

    except Integration.DoesNotExist:
        raise BadRequestException("please connect the app first.")

    return HttpResponse(status=204)


@api_view(["GET", "PATCH"])
def get_or_patch_crm_data_by_id(request, obj_type, obj_id):
    api = 'crm'
    if request.method == 'PATCH':
        input_data = request.data
        if 'model' not in input_data:
            raise BadRequestException("Please include model object in the request body.")
        if 'instance_id' not in input_data:
            raise BadRequestException("Please include instance_id in the request body.")
        if input_data:
            instance_id = input_data.get('instance_id', None)
        integration, token = auth.get_auth(instance_id)
        if not token or not integration:
            raise UnauthorizedException("You have not connected the app " + instance_id)
        package_name = "integrations.connectors." + integration.name + "." + api + ".request_data"
        mod = importlib.import_module(package_name)
        data = mod.update_object(token, integration, obj_id, obj_type, input_data['model'])
        if not data:
            raise BadRequestException(
                "Api action is not supported for " + integration.name + " with object type " + obj_type)
        if 'error' in data:
            return JsonResponse(data, status=data['error'].get('status_code', 400))
        return JsonResponse(data)
    elif request.method == 'GET':
        url_params = request.GET.urlencode()
        custom_fields = []
        include_field_properties = False
        instance_id = None
        if url_params:
            url_params_dict = parse_qs(url_params)
            if 'include_field_properties' in url_params_dict and url_params_dict['include_field_properties'][
                0].lower() == 'true':
                include_field_properties = True
            if 'fields' in url_params_dict:
                custom_fields = url_params_dict['fields']
            if 'instance_id' in url_params_dict:
                instance_id = url_params_dict['instance_id'][0]
        if not instance_id:
            raise BadRequestException("Please include instance_id in the query parameter.")
        integration, token = auth.get_auth(instance_id)
        if not integration or not token:
            raise UnauthorizedException("You have not connected the app " + instance_id)

        package_name = "integrations.connectors." + integration.name + "." + api + ".request_data"
        mod = importlib.import_module(package_name)
        data = mod.get_object_by_id(token, integration, obj_type, obj_id, include_field_properties, custom_fields)
        if not data:
            raise BadRequestException(
                "Api action is not supported for " + integration.name + " with object type " + obj_type)
        if 'error' in data:
            return JsonResponse(data, status=data['error'].get('status_code', 400))
        return JsonResponse(data)


@api_view(["GET", "POST"])
def get_or_create_crm_data(request, obj_type):
    api = 'crm'
    if request.method == 'POST':
        input_data = request.data
        if 'model' not in input_data:
            raise BadRequestException("Please include model object in request body.")
        if 'instance_id' not in input_data:
            raise BadRequestException("Please include instance_id in the request body.")
        instance_id = None
        if input_data:
            instance_id = input_data.get('instance_id', None)
        integration, token = auth.get_auth(instance_id)
        if not token or not integration:
            raise UnauthorizedException("You have not connected the app " + instance_id)
        package_name = "integrations.connectors." + integration.name + "." + api + ".request_data"
        mod = importlib.import_module(package_name)
        data = mod.create_object(token, integration, obj_type, input_data['model'])
        if not data:
            raise BadRequestException(
                "Api action is not supported for " + integration.name + " with object type " + obj_type)
        if 'error' in data:
            return JsonResponse(data, status=data['error'].get('status_code', 400))
        return JsonResponse(data)
    elif request.method == 'GET':

        url_params = request.GET.urlencode()
        custom_fields = []
        obj_ids = []
        include_field_properties = False
        instance_id = None
        owner_id = None
        page_size = None
        cursor = None
        created_before = None
        created_after = None
        modified_before = None
        modified_after = None
        if url_params:
            url_params_dict = parse_qs(url_params)
            if 'include_field_properties' in url_params_dict and url_params_dict['include_field_properties'][
                0].lower() == 'true':
                include_field_properties = True
            if 'fields' in url_params_dict:
                custom_fields = url_params_dict['fields']
            if 'instance_id' in url_params_dict:
                instance_id = url_params_dict['instance_id'][0]
            if 'ids' in url_params_dict:
                obj_ids = url_params_dict['ids']
                if len(obj_ids) > 100:
                    raise BadRequestException('number of ids can not exceed 100')
            if 'owner_id' in url_params_dict:
                owner_id = url_params_dict['owner_id'][0]
            if 'page_size' in url_params_dict:
                page_size = url_params_dict['page_size'][0]
                if int(page_size) > 100:
                    raise BadRequestException('page_size can not exceed 100')
            if 'cursor' in url_params_dict:
                cursor = url_params_dict['cursor'][0]
            if 'created_before' in url_params_dict:
                created_before = url_params_dict['created_before'][0]
            if 'created_after' in url_params_dict:
                created_after = url_params_dict['created_after'][0]
            if 'modified_before' in url_params_dict:
                modified_before = url_params_dict['modified_before'][0]
            if 'modified_after' in url_params_dict:
                modified_after = url_params_dict['modified_after'][0]
        if not instance_id:
            raise BadRequestException("Please include instance_id in the query parameter.")
        integration, token = auth.get_auth(instance_id)
        if not token or not integration:
            raise UnauthorizedException("You have not connected the app " + instance_id)
        package_name = "integrations.connectors." + integration.name + "." + api + ".request_data"
        mod = importlib.import_module(package_name)
        data = mod.get_objects(token, integration, obj_type, include_field_properties, custom_fields, obj_ids, owner_id,
                               created_before,
                               created_after, modified_before, modified_after, page_size,
                               cursor)
        if not data:
            raise BadRequestException(
                "Api action is not supported for " + integration.name + " with object type " + obj_type)
        if 'error' in data:
            return JsonResponse(data, status=data['error'].get('status_code', 400))
        return JsonResponse(data)


@api_view(["GET"])
def get_crm_field_properties(request, obj_type):
    api = 'crm'
    url_params = request.GET.urlencode()
    instance_id = None
    if url_params:
        url_params_dict = parse_qs(url_params)
        if 'instance_id' in url_params_dict:
            instance_id = url_params_dict['instance_id'][0]

    if not instance_id:
        raise BadRequestException("Please include instance_id in the query parameter.")
    integration, token = auth.get_auth(instance_id)
    if not token or not integration:
        raise UnauthorizedException("You have not connected the app " + instance_id)
    package_name = "integrations.connectors." + integration.name + "." + api + ".request_data"
    mod = importlib.import_module(package_name)
    data = mod.get_field_properties(token, integration, obj_type)
    if not data:
        raise BadRequestException(
            "Api action is not supported for " + integration.name + " with object type " + obj_type)
    if 'error' in data:
        return JsonResponse(data, status=data['error'].get('status_code', 400))
    return JsonResponse(data)


@api_view(["GET"])
def reindex_data(request, schema):
    integrations = Integration.objects.filter(enabled=True)
    for i in integrations:
        config = auth.get_config(i.name)
        if not config:
            continue
        for a in config['api']:
            if a['schema'] == schema:
                templates = Template.objects.filter(schema=schema, deleted=False)
                if len(templates) == 0:
                    return redirect('/config/' + schema)
                for template in templates:
                    index_data_diff(schema, i.instance_id, template.obj_type)
    return HttpResponse(status=204)


def index_data_reset(api, instance_id, obj_type, template):
    integration, token = auth.get_auth(instance_id)
    auth.update_last_sync(instance_id, obj_type)
    index_fields = get_params(template)
    documents = []
    load_data(api, token, integration, obj_type, index_fields, template, documents, None, None)
    vector_utils.index_documents(documents, instance_id, obj_type)


def index_data_diff(schema, instance_id, obj_type):
    integration, token = auth.get_auth(instance_id)
    auth.update_last_sync(instance_id, obj_type)
    try:
        _template = Template.objects.get(schema=schema, obj_type=obj_type)
        template = _template.content
    except Template.DoesNotExist:
        return
    documents = []
    last_sync_at = None
    if integration.sync_status:
        sync_status = json.loads(integration.sync_status)
        if obj_type in sync_status:
            last_sync_at = sync_status[obj_type]['sync_at']
    index_fields = get_params(template)
    load_data(schema, token, integration, obj_type, index_fields, template, documents, None, last_sync_at)
    vector_utils.index_documents(documents, integration.instance_id, obj_type)


def load_data(schema, token, integration, obj_type, index_fields, template, documents, cursor, last_sync_at):
    package_name = "integrations.connectors." + integration.name + "." + schema + ".request_data"
    mod = importlib.import_module(package_name)
    data = mod.load_objects(token, integration, obj_type, last_sync_at, cursor)
    if 'error' in data:
        if data['error']['status_code'] == 429:
            sleep(15)
            load_data(schema, token, integration, obj_type, index_fields, template, documents, cursor, last_sync_at)
    else:
        if len(data['results']) == 0:
            return
        for d in data['results']:
            document = {'id': d['id']}
            _template = copy.deepcopy(template)
            for field in index_fields:
                if field in d['data']:
                    if not isinstance(d['data'][field], list):
                        _template = _template.replace('{{' + field + '}}', str(d['data'][field]))
            document['text'] = _template
            documents.append(document)
        if 'next_cursor' in data:
            cursor = data['next_cursor']
            load_data(schema, token, integration, obj_type, index_fields, template, documents, cursor, last_sync_at)


@api_view(["GET"])
def get_index_data(request):
    url_params = request.GET.urlencode()
    instance_id = None
    query = None
    if url_params:
        url_params_dict = parse_qs(url_params)
        if 'instance_id' in url_params_dict:
            instance_id = url_params_dict['instance_id'][0]
        if 'query' in url_params_dict:
            query = url_params_dict['query'][0]
    if not instance_id:
        raise BadRequestException("Please include instance_id in the query parameter.")
    results = vector_utils.query_documents(query, instance_id)
    return JsonResponse(results)

