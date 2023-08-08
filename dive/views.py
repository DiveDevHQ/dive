from integrations.models import Integration
from integrations.models import Template
from integrations import authentication as auth
from django.shortcuts import redirect
import uuid
from django.http import JsonResponse
from datetime import datetime, timezone, timedelta
from dive.api.exceptions import UnauthorizedException
import importlib
from dive.api.exceptions import BadRequestException
from urllib.parse import parse_qs, urlencode
from rest_framework.decorators import action, api_view
from django.http import HttpResponse
from dive.indices.service_context import ServiceContext
from dive.retrievers.query_context import QueryContext
from dive.indices.index_context import IndexContext
from dive.types import EmbeddingConfig
from langchain.schema import Document
from dive.constants import DEFAULT_COLLECTION_NAME, DEFAULT_CHUNKING_TYPE
from dive.util.model_util import get_llm, get_embeddings

import json
import environ
import copy
from dive.api.utils import send_message_socket
from time import sleep
from django.shortcuts import render
import os
from pathlib import Path

env = environ.Env()
environ.Env.read_env()


def index(request):
    context = {
        "home_url": env.str('HOME_URL', default='http://localhost:3000'),
    }
    return render(request, "index.html", context)


def about(request):
    return HttpResponse(status=204)


def get_connected_apps(request, account_id):
    integrations = Integration.objects.filter(enabled=True, account_id=account_id)
    connectors = []
    for i in integrations:
        connectors.append(
            {'account_id': i.account_id, 'connector_id': i.connector_id, 'app': i.name, 'sync_status': i.sync_status})
    return JsonResponse(connectors, safe=False)


def initialize_vector(request):
    PINECONE_API_KEY = env.str('PINECONE_API_KEY', default='') or os.environ.get('PINECONE_API_KEY', '')
    PINECONE_ENV = env.str('PINECONE_ENV', default='') or os.environ.get('PINECONE_ENV', '')
    PINECONE_INDEX_DIMENSIONS = env.str('PINECONE_INDEX_DIMENSIONS', default='512') or os.environ.get(
        'PINECONE_INDEX_DIMENSIONS', '512')
    if PINECONE_API_KEY:
        import_err_msg = (
            "`pinecone` package not found, please run `pip install pinecone`"
        )
        try:
            import pinecone
            pinecone.init(
                api_key=PINECONE_API_KEY,  # find at app.pinecone.io
                environment=PINECONE_ENV,  # next to api key in console
            )

            if DEFAULT_COLLECTION_NAME not in pinecone.list_indexes():
                pinecone.create_index(
                    name=DEFAULT_COLLECTION_NAME,
                    metric="cosine",
                    dimension=int(PINECONE_INDEX_DIMENSIONS))

        except ImportError:
            raise ImportError(import_err_msg)
    '''
    else:
        CHROMA_PERSIST_DIR = env.str('CHROMA_PERSIST_DIR', default='db') or os.environ.get('CHROMA_PERSIST_DIR', 'db')
        import_err_msg = (
            "`chromadb` package not found, please run `pip install chromadb`"
        )
        try:
            import chromadb
            client_settings = chromadb.config.Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=CHROMA_PERSIST_DIR
            )
            client = chromadb.Client(
                client_settings
            )
            client.get_collection(DEFAULT_COLLECTION_NAME)
        except ImportError:
            raise ImportError(import_err_msg)
        except KeyError:
            client.create_collection(DEFAULT_COLLECTION_NAME)
    '''
    return HttpResponse(status=204)


@api_view(["POST"])
def authorization_api(request, app):
    integration_config = auth.get_config(app)
    if not integration_config:
        raise BadRequestException('provider ' + app + ' is not supported')
    connector_id = request.data.get('connector_id', '')
    if not connector_id:
        raise BadRequestException('connector_id is required')
    account_id = request.data.get('account_id', '')

    if not account_id:
        raise BadRequestException('account_id is required')
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
            integration = Integration.objects.get(name=app, connector_id=connector_id)
            integration.client_id = client_id
            integration.client_secret = client_secret
            integration.scope = scope_str
            integration.redirect_uri = redirect_uri
            integration.connector_id = connector_id
            integration.account_id = account_id
            integration.save()

        except Integration.DoesNotExist:
            integration = Integration(name=app,
                                      client_id=client_id,
                                      client_secret=client_secret,
                                      scope=scope_str,
                                      redirect_uri=redirect_uri,
                                      connector_id=connector_id,
                                      account_id=account_id)
            integration.save()

        url_encoding = urlencode(url_dict)
        return JsonResponse({'redirect': integration_config['authorization_url'] + "?" + url_encoding})

    if integration_config['auth_method'] == 'APIKEY':
        api_key = request.data.get('api_key', '')
        if not api_key:
            raise BadRequestException('api_key is required')
        try:
            integration = Integration.objects.get(name=app, connector_id=connector_id)
            integration.api_key = api_key
            integration.enabled = True
            integration.connector_id = connector_id
            integration.account_id = account_id
            integration.redirect_uri = redirect_uri
            integration.save()
        except Integration.DoesNotExist:
            integration = Integration(name=app,
                                      api_key=api_key, enabled=True, connector_id=connector_id,
                                      redirect_uri=redirect_uri, account_id=account_id)

            integration.save()
    if integration_config['auth_method'] == 'NOAUTH':
        try:
            integration = Integration.objects.get(name=app, connector_id=connector_id)
            integration.enabled = True
            integration.connector_id = connector_id
            integration.account_id = account_id
            integration.redirect_uri = redirect_uri
            integration.save()
        except Integration.DoesNotExist:
            integration = Integration(name=app,
                                      enabled=True, connector_id=connector_id,
                                      redirect_uri=redirect_uri, account_id=account_id)
            integration.save()
        return JsonResponse({'redirect': redirect_uri})


@api_view(["POST"])
def callback_api(request):
    authorization_code = request.data.get('code', '')
    connector_id = request.data.get('connector_id', '')
    if not authorization_code:
        raise BadRequestException("code is required")
    if not connector_id:
        raise BadRequestException("connector_id is required")
    try:
        integration = Integration.objects.get(connector_id=connector_id)
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
            raise BadRequestException(token_result.json_body)

    except Integration.DoesNotExist:
        raise BadRequestException("please connect the app first.")

    return HttpResponse(status=204)


@api_view(["GET", "PATCH"])
def get_or_patch_crm_data_by_id(request, obj_type, obj_id):
    module = 'crm'
    if request.method == 'PATCH':
        input_data = request.data
        if 'model' not in input_data:
            raise BadRequestException("Please include model object in the request body.")
        if 'connector_id' not in input_data:
            raise BadRequestException("Please include connector_id in the request body.")
        if input_data:
            connector_id = input_data.get('connector_id', None)
            account_id = input_data.get('account_id', 'self')
        integration, token = auth.get_auth(account_id, connector_id)
        if not token or not integration:
            raise UnauthorizedException("You have not connected the app " + connector_id)
        package_name = "integrations.connectors." + integration.name + "." + module + ".request_data"
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
        connector_id = None
        account_id = 'self'
        if url_params:
            url_params_dict = parse_qs(url_params)
            if 'include_field_properties' in url_params_dict and url_params_dict['include_field_properties'][
                0].lower() == 'true':
                include_field_properties = True
            if 'fields' in url_params_dict:
                custom_fields = url_params_dict['fields']
            if 'connector_id' in url_params_dict:
                connector_id = url_params_dict['connector_id'][0]
            if 'account_id' in url_params_dict:
                account_id = url_params_dict['account_id'][0]
        if not connector_id:
            raise BadRequestException("Please include connector_id in the query parameter.")
        integration, token = auth.get_auth(account_id, connector_id)
        if not integration or not token:
            raise UnauthorizedException("You have not connected the app " + connector_id)

        package_name = "integrations.connectors." + integration.name + "." + module + ".request_data"
        mod = importlib.import_module(package_name)
        data = mod.get_object_by_id(token, integration, obj_type, obj_id, include_field_properties, custom_fields, None)
        if not data:
            raise BadRequestException(
                "Api action is not supported for " + integration.name + " with object type " + obj_type)
        if 'error' in data:
            return JsonResponse(data, status=data['error'].get('status_code', 400))
        return JsonResponse(data)


@api_view(["GET", "POST"])
def get_or_create_crm_data(request, obj_type):
    module = 'crm'
    if request.method == 'POST':
        input_data = request.data
        if 'model' not in input_data:
            raise BadRequestException("Please include model object in request body.")
        if 'connector_id' not in input_data:
            raise BadRequestException("Please include connector_id in the request body.")
        connector_id = None
        account_id = 'self'
        if input_data:
            connector_id = input_data.get('connector_id', None)
            account_id = input_data.get('account_id', 'self')
        integration, token = auth.get_auth(account_id, connector_id)
        if not token or not integration:
            raise UnauthorizedException("You have not connected the app " + connector_id)
        package_name = "integrations.connectors." + integration.name + "." + module + ".request_data"
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
        connector_id = None
        account_id = 'self'
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
            if 'connector_id' in url_params_dict:
                connector_id = url_params_dict['connector_id'][0]
            if 'account_id' in url_params_dict:
                account_id = url_params_dict['account_id'][0]
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
        if not connector_id:
            raise BadRequestException("Please include connector_id in the query parameter.")
        integration, token = auth.get_auth(account_id, connector_id)
        if not token or not integration:
            raise UnauthorizedException("You have not connected the app " + connector_id)
        package_name = "integrations.connectors." + integration.name + "." + module + ".request_data"
        mod = importlib.import_module(package_name)
        data = mod.get_objects(token, integration, obj_type, include_field_properties, custom_fields, obj_ids, owner_id,
                               created_before,
                               created_after, modified_before, modified_after, page_size,
                               cursor, None)
        if not data:
            raise BadRequestException(
                "Api action is not supported for " + integration.name + " with object type " + obj_type)
        if 'error' in data:
            return JsonResponse(data, status=data['error'].get('status_code', 400))
        return JsonResponse(data)


@api_view(["GET"])
def get_crm_field_properties(request, obj_type):
    module = 'crm'
    url_params = request.GET.urlencode()
    connector_id = None
    account_id = 'self'
    if url_params:
        url_params_dict = parse_qs(url_params)
        if 'connector_id' in url_params_dict:
            connector_id = url_params_dict['connector_id'][0]
        if 'account_id' in url_params_dict:
            account_id = url_params_dict['account_id'][0]
    if not connector_id:
        raise BadRequestException("Please include connector_id in the query parameter.")
    integration, token = auth.get_auth(account_id, connector_id)
    if not token or not integration:
        raise UnauthorizedException("You have not connected the app " + connector_id)
    package_name = "integrations.connectors." + integration.name + "." + module + ".request_data"
    mod = importlib.import_module(package_name)
    data = mod.get_field_properties(token, integration, obj_type)
    if not data:
        raise BadRequestException(
            "Api action is not supported for " + integration.name + " with object type " + obj_type)
    if 'error' in data:
        return JsonResponse(data, status=data['error'].get('status_code', 400))
    return JsonResponse(data)


@api_view(["PUT"])
def sync_instance_data(request, app, account_id, connector_id):
    templates = Template.objects.filter(app=app, account_id=account_id, deleted=False)
    if len(templates) == 0:
        auth.update_sync_error(account_id, connector_id, {'id': 'Missing data schema', 'status_code': 400,
                                                          'message': 'Please add schema from Connectors tab'})

    for template in templates:
        chunking_type = None
        chunk_size = None
        chunk_overlap = None
        if template.chunking_type:
            ct = json.loads(template.chunking_type)
            if not ct:
                chunking_type = DEFAULT_CHUNKING_TYPE
            else:
                chunking_type = ct.get('chunking_type', None)
                chunk_size = ct.get('chunk_size', None)
                chunk_overlap = ct.get('chunk_overlap', None)
            if chunk_size:
                chunk_size = int(chunk_size)
            if chunk_overlap:
                chunk_overlap = int(chunk_overlap)
        index_data(template.module, account_id, connector_id, template.obj_type, template.schema, False, chunking_type,
                   chunk_size,
                   chunk_overlap)
    return HttpResponse(status=204)


@api_view(["PUT"])
def clear_instance_data(request, app, account_id, connector_id):
    auth.clear_sync_status(account_id, connector_id)
    index_context = IndexContext.from_defaults()
    index_context.delete(filter={'data_id': str(account_id) + str(connector_id)})
    return HttpResponse(status=204)


def index_data(module, account_id, connector_id, obj_type, schema, reload, chunking_type, chunk_size,
               chunk_overlap):
    integration, token = auth.get_auth(account_id, connector_id)
    obj_last_sync_at = None
    if not reload:
        obj_last_sync_at = auth.get_last_sync_at(account_id, connector_id, obj_type)

    auth.update_last_sync(account_id, connector_id, obj_type, False)
    data_id = str(integration.account_id) + str(connector_id)
    metadata = {'account_id': integration.account_id, 'connector_id': connector_id, 'data_id': data_id,
                'obj_type': obj_type}
    embedding_model = EmbeddingConfig()
    embedding_model.chunking_type = chunking_type
    embedding_model.chunk_size = chunk_size or embedding_model.chunk_size
    embedding_model.chunk_overlap = chunk_overlap or embedding_model.chunk_overlap

    service_context = ServiceContext.from_defaults(embed_config=embedding_model, embeddings=get_embeddings(),
                                                   llm=get_llm())
    load_data(module, token, integration, obj_type, schema, None, obj_last_sync_at, metadata, service_context)
    auth.update_last_sync(account_id, connector_id, obj_type, True)


def load_data(module, token, integration, obj_type, schema, cursor, last_sync_at, metadata, service_context):
    package_name = "integrations.connectors." + integration.name + "." + module + ".request_data"
    mod = importlib.import_module(package_name)
    data = mod.load_objects(token, integration, obj_type, last_sync_at, cursor, schema)
    if 'error' in data:
        if data['error']['status_code'] == 429:
            sleep(15)
            load_data(module, token, integration, obj_type, schema, cursor, last_sync_at, metadata, service_context)
    else:
        if len(data['results']) == 0:
            return
        _documents = []
        _ids = []
        for d in data['results']:
            _metadata = metadata
            if 'metadata' in d:
                _metadata.update(d['metadata'])
            document = Document(page_content=str(d['data']), metadata=_metadata)
            _documents.append(document)
            _ids.append(d['id'])

        IndexContext.from_documents(documents=_documents, ids=_ids, service_context=service_context)
        if 'next_cursor' in data:
            cursor = data['next_cursor']
            load_data(module, token, integration, obj_type, schema, cursor, last_sync_at, metadata, service_context)


@api_view(["GET"])
def get_query_data(request):
    url_params = request.GET.urlencode()
    connector_id = None
    account_id = None
    query = None
    top_k = None
    instruction = None
    query_type = None
    if url_params:
        url_params_dict = parse_qs(url_params)
        if 'connector_id' in url_params_dict and url_params_dict['connector_id'][0]:
            connector_id = url_params_dict['connector_id'][0]
        if 'account_id' in url_params_dict and url_params_dict['account_id'][0]:
            account_id = url_params_dict['account_id'][0]
        if 'query_text' in url_params_dict:
            query = url_params_dict['query_text'][0]
        if 'top_k' in url_params_dict:
            top_k = url_params_dict['top_k'][0]
        if 'instruction' in url_params_dict:
            instruction = url_params_dict['instruction'][0]
        if 'query_type' in url_params_dict:
            query_type = url_params_dict['query_type'][0]

    if not account_id:
        raise BadRequestException("Please include account_id in the query parameter.")
    if not query:
        raise BadRequestException("Please include query_text in query parameter.")

    service_context = ServiceContext.from_defaults(embeddings=get_embeddings(), llm=get_llm(), instruction=instruction)
    query_context = QueryContext.from_defaults(service_context=service_context)

    k = None
    if top_k:
        k = int(top_k)
    if connector_id:
        where = {'data_id': str(account_id)+str(connector_id)}
    else:
        where = {'account_id': str(account_id)}
    try:
        data = query_context.query(query=query, k=k, filter=where)
    except ValueError:
        error_data = {'error': {}}
        error_data['error']['id'] = 'Not Found'
        error_data['error']['message'] = 'Requested vector data does not exist'
        error_data['error']['status_code'] = 404
        return JsonResponse(error_data, safe=False)

    result_text = ''
    top_chunks = []
    if len(data) > 0:
        for d in data:
            top_chunks.append(d.page_content)
        if query_type == 'summary':
            result_text = query_context.summarization(documents=data)
        else:
            result_text = query_context.question_answer(query=query, documents=data)

    return JsonResponse({'result': result_text, 'top_chunks': top_chunks}, safe=False)


chat_history = {}
chat_queue = {}


@api_view(["GET", "DELETE"])
def get_or_delete_message_queue(request, user_id):
    if request.method == 'GET':
        if user_id in chat_queue:
            return JsonResponse({'hasMessage': True, 'incomingAt': chat_queue[user_id]}, safe=False)
        return JsonResponse({'hasMessage': False}, safe=False)
    elif request.method == 'DELETE':
        if user_id in chat_queue:
            del chat_queue[user_id]
        return HttpResponse(status=204)


@api_view(["POST"])
def add_message(request):
    user_id = None
    text = None
    message_id = None
    input_data = request.data
    if 'userId' in input_data and input_data['userId']:
        user_id = input_data['userId']
    if 'text' in input_data and input_data['text']:
        text = input_data['text']
    if 'messageId' in input_data and input_data['messageId']:
        message_id = input_data['messageId']
    if not message_id:
        message_id = str(uuid.uuid4())

    if not user_id in chat_history:
        chat_history[user_id] = []

    timestamp = int((datetime.now() - datetime(1970, 1, 1)).total_seconds() * 1000)
    service_context = ServiceContext.from_defaults(embeddings=get_embeddings(), llm=get_llm(), instruction=None)
    query_context = QueryContext.from_defaults(service_context=service_context)

    data = query_context.query(query=text, k=4, filter={'connector_id': 'example'})

    result_text = ''
    top_chunks = []
    if len(data) > 0:
        for d in data:
            top_chunks.append(d.page_content)
        result_text = query_context.question_answer(query=text, documents=data)

    if result_text:
        chat_history[user_id].append({'messageId': str(uuid.uuid4()), 'text': result_text, 'createdAt': timestamp})
        if not user_id in chat_queue:
            chat_queue[user_id] = timestamp
    send_message_socket(user_id)
    return JsonResponse([], safe=False)


@api_view(["POST"])
def get_message(request, user_id):
    incoming_at = 0
    input_data = request.data
    if 'incomingAt' in input_data and input_data['incomingAt']:
        incoming_at = input_data['incomingAt']
    print(incoming_at)
    if not user_id in chat_history:
        return JsonResponse({'messages': []}, safe=False)

    messages = [x for x in chat_history[user_id] if int(x['createdAt']) >= int(incoming_at)]
    return JsonResponse(messages, safe=False)


@api_view(["GET"])
def get_obj_schemas(request, app, module):
    base_path = Path(__file__).parent.parent
    folder_path = str(base_path) + '/integrations/connectors/' + app + '/' + module + '/schemas/'
    dir_list = os.listdir(folder_path)
    schemas = []
    for path in dir_list:
        with open(folder_path + path) as f:
            field_dict = json.load(f)
            schemas.append({'app': app, 'module': module, 'obj_type': os.path.splitext(path)[0], 'schema': field_dict})
    return JsonResponse(schemas, safe=False)


@api_view(["GET"])
def get_obj_templates(request, app, module, account_id):
    templates = Template.objects.filter(module=module, app=app, deleted=False, account_id=account_id)
    schemas = []
    for template in templates:
        schemas.append({'template_id': template.id, 'app': app, 'module': module, 'obj_type': template.obj_type,
                        'schema': json.loads(template.schema) if template.schema else None,
                        'chunking_type': json.loads(template.chunking_type) if template.chunking_type else None})
    return JsonResponse(schemas, safe=False)


@api_view(["POST"])
def add_obj_template(request):
    app = request.data.get('app', '')
    module = request.data.get('module', '')
    obj_type = request.data.get('obj_type', '')
    schema = json.dumps(request.data.get('schema', ''))
    account_id = request.data.get('account_id', '')
    chunking_type = json.dumps(request.data.get('chunking_type', None))
    result = {'app': app, 'module': module, 'obj_type': obj_type,'chunking_type':json.loads(chunking_type),
              'schema': json.loads(schema)}
    try:
        template = Template.objects.get(module=module, app=app, obj_type=obj_type, account_id=account_id)
        template.schema = schema
        template.account_id = account_id
        template.chunking_type = chunking_type
        template.deleted = False
        template.save()
        result['template_id'] = template.id

    except Template.DoesNotExist:
        template = Template(app=app,
                            module=module,
                            obj_type=obj_type,
                            schema=schema,
                            account_id=account_id,
                            chunking_type=chunking_type)
        template.save()

        result['template_id'] = Template.objects.last().id

    return JsonResponse(result, safe=False)


@api_view(["DELETE", "PATCH"])
def patch_or_delete_template(request, template_id):
    if request.method == 'PATCH':
        try:
            template = Template.objects.get(id=template_id)
            template.chunking_type = json.dumps(request.data.get('chunking_type', None))

            template.save()

        except Template.DoesNotExist:
            return HttpResponse(status=404)
    elif request.method == 'DELETE':
        try:
            template = Template.objects.get(id=template_id)
            template.deleted = True
            template.save()
        except Template.DoesNotExist:
            return HttpResponse(status=404)
    return HttpResponse(status=204)
