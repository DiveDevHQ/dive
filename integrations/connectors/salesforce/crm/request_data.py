import json
import integrations.connectors.connectors_utils as util
import dive.api.request_utils as ru
from pathlib import Path
from datetime import datetime
import copy
import os


def get_object_by_id(auth, app, obj_type, obj_id, include_field_properties, custom_fields, schema):
    if schema:
        field_dict = json.loads(schema)
    else:
        base_path = Path(__file__).parent
        try:
            with open(str(base_path) + '/schemas/' + obj_type + '.json') as f:
                field_dict = json.load(f)
        except FileNotFoundError:
            return

    config = json.loads(app.auth_json)
    instance_url = config.get('instance_url', None)
    match obj_type:
        case 'accounts' | 'contacts' | 'users' | 'opportunities':
            if obj_type == 'opportunities':
                obj_type_singular = 'Opportunity'
            else:
                obj_type_singular = capitalize_first_letter(obj_type[:-1])
            return execute_get_object_by_id(auth, instance_url, obj_id, obj_type, obj_type_singular, field_dict,
                                            custom_fields,
                                            include_field_properties)
        case 'stages':
            return get_stage_by_id(auth, instance_url, obj_id, field_dict, include_field_properties)
        case _:
            return


def get_objects(auth, app, obj_type, include_field_properties, custom_fields, obj_ids: [], owner_id, created_before,
                created_after, modified_before, modified_after, page_size, cursor, schema):
    if schema:
        field_dict = json.loads(schema)
    else:
        base_path = Path(__file__).parent
        try:
            with open(str(base_path) + '/schemas/' + obj_type + '.json') as f:
                field_dict = json.load(f)
        except FileNotFoundError:
            return

    config = json.loads(app.auth_json)
    instance_url = config.get('instance_url', None)

    if len(obj_ids) > 0:
        match obj_type:
            case 'accounts' | 'contacts' | 'users' | 'opportunities':
                if obj_type == 'opportunities':
                    obj_type_singular = 'Opportunity'
                else:
                    obj_type_singular = capitalize_first_letter(obj_type[:-1])
                return execute_get_objects_by_ids(auth, instance_url, obj_ids, obj_type, obj_type_singular, field_dict,
                                                  custom_fields,
                                                  include_field_properties)
            case 'stages':
                return get_stages(auth, instance_url, obj_ids, field_dict, include_field_properties)
            case _:
                return
    else:
        match obj_type:

            case 'accounts' | 'contacts' | 'users' | 'opportunities':
                if obj_type == 'opportunities':
                    obj_type_singular = 'Opportunity'
                else:
                    obj_type_singular = capitalize_first_letter(obj_type[:-1])
                return execute_get_objects(auth, instance_url, obj_type, obj_type_singular, field_dict, custom_fields,
                                           include_field_properties,
                                           owner_id,
                                           created_before, created_after, modified_before, modified_after,
                                           page_size, cursor)
            case 'stages':
                return get_stages(auth, instance_url, [], field_dict, include_field_properties)
            case _:
                return


def load_objects(auth, app, obj_type, modified_after, cursor, schema):
    return get_objects(auth, app, obj_type, False, [], [], None,
                       None,
                       None, None, modified_after, 100,
                       cursor, schema)


def create_object(auth, app, obj_type, input_data):
    base_path = Path(__file__).parent
    try:
        with open(str(base_path) + '/schemas/' + obj_type + '.json') as f:
            field_dict = json.load(f)
    except FileNotFoundError:
        return

    config = json.loads(app.auth_json)
    instance_url = config.get('instance_url', None)
    match obj_type:
        case 'accounts' | 'contacts' | 'opportunities':
            if obj_type == 'opportunities':
                obj_type_singular = 'Opportunity'
            else:
                obj_type_singular = capitalize_first_letter(obj_type[:-1])
            return execute_create_object(auth, instance_url, obj_type_singular, input_data, field_dict)
        case _:
            return


def update_object(auth, app, obj_id, obj_type, input_data):
    base_path = Path(__file__).parent
    try:
        with open(str(base_path) + '/schemas/' + obj_type + '.json') as f:
            field_dict = json.load(f)
    except FileNotFoundError:
        return

    config = json.loads(app.auth_json)
    instance_url = config.get('instance_url', None)

    match obj_type:
        case 'accounts' | 'contacts' | 'opportunities':
            if obj_type == 'opportunities':
                obj_type_singular = 'Opportunity'
            else:
                obj_type_singular = capitalize_first_letter(obj_type[:-1])
            return execute_update_object(auth, instance_url, obj_id, obj_type_singular, input_data, field_dict)

        case _:
            return


def get_field_properties(auth, app, obj_type):
    base_path = Path(__file__).parent
    try:
        with open(str(base_path) + '/schemas/' + obj_type + '.json') as f:
            field_dict = json.load(f)
    except FileNotFoundError:
        return

    config = json.loads(app.auth_json)
    instance_url = config.get('instance_url', None)

    match obj_type:
        case 'accounts' | 'contacts' | 'opportunities' | 'users' | 'stages':
            if obj_type == 'opportunities':
                obj_type_singular = 'Opportunity'
            else:
                obj_type_singular = capitalize_first_letter(obj_type[:-1])
            return execute_get_field_properties(auth, instance_url, obj_type, obj_type_singular, field_dict)

        case _:
            return


def execute_get_object_by_id(auth, instance_url, obj_id, obj_type_plural, obj_type_singular, fields, custom_fields,
                             include_field_properties):
    url = instance_url + '/services/data/v57.0/graphql'
    properties = get_properties_from_model(fields, custom_fields)
    obj = query_object_by_id(auth, url, obj_id, obj_type_plural, obj_type_singular, properties, fields,
                             custom_fields)
    result = {'id': obj_id}
    properties_details = get_properties(auth, instance_url, obj_type_singular)
    if 'data' in obj:
        if obj_type_plural == 'accounts' or obj_type_plural == 'contacts' or obj_type_plural == 'opportunities':
            if obj['data'].get('last_activity_at', None):
                get_normalized_data(obj['data'], 'last_activity_at')
            elif obj_type_plural == 'opportunities' and obj['data'].get('close_date', None):
                get_normalized_data(obj['data'], 'close_date')
        if not include_field_properties:
            datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)
            for df in datetime_fields:
                obj['data'][df] = get_normalized_datetime(obj['data'].get(df, None))
            result['data'] = obj['data']
        elif include_field_properties:
            properties_with_options = get_properties_with_options(auth, instance_url, obj_type_singular,
                                                                  properties_details,
                                                                  properties)
            fields_properties = get_fields_properties(obj_type_plural, properties_with_options, fields, custom_fields)
            for p in fields_properties:
                if p['field_type'] == 'datetime':
                    obj['data'][p['id']] = get_normalized_datetime(obj['data'].get(p['id'], None))
                p['value'] = obj['data'].get(p['id'], None)
            result['data'] = obj['data']
            result['field_properties'] = fields_properties
    elif 'error' in obj:
        result['error'] = obj['error']
    return result


def execute_get_objects(auth, instance_url, obj_type_plural, obj_type_singular, fields, custom_fields,
                        include_field_properties, owner_id,
                        created_before,
                        created_after, modified_before, modified_after, limit, cursor):
    properties = get_properties_from_model(fields, custom_fields)

    if not limit:
        limit = '100'
    url = instance_url + '/services/data/v57.0/graphql'
    objects = query_objects(auth, url, obj_type_plural, obj_type_singular, properties, fields, custom_fields, owner_id,
                            created_before,
                            created_after, modified_before, modified_after, limit, cursor)

    if 'error' in objects:
        return {'results': [], 'error': objects['error']}

    properties_details = get_properties(auth, instance_url, obj_type_singular)

    datetime_fields = []
    if not include_field_properties:
        datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)

    for obj in objects['results']:
        if 'last_activity_at' in fields and obj['data'].get('last_activity_at', None):
            get_normalized_data(obj['data'], 'last_activity_at')
        if 'close_date' in fields and obj['data'].get('close_date', None):
            get_normalized_data(obj['data'], 'close_date')
        for df in datetime_fields:
            obj['data'][df] = get_normalized_datetime(obj['data'].get(df, None))

    if include_field_properties:
        properties_with_options = get_properties_with_options(auth, instance_url, obj_type_singular,
                                                              properties_details,
                                                              properties)
        fields_properties = get_fields_properties(obj_type_plural, properties_with_options, fields, custom_fields)
        for obj in objects['results']:
            obj['field_properties'] = copy.deepcopy(fields_properties)
            for p in obj['field_properties']:
                if p['field_type'] == 'datetime':
                    obj['data'][p['id']] = get_normalized_datetime(obj['data'].get(p['id'], None))
                p['value'] = obj['data'].get(p['id'], None)

    return objects


def execute_get_objects_by_ids(auth, instance_url, obj_ids: [], obj_type_plural, obj_type_singular, fields,
                               custom_fields,
                               include_field_properties):
    url = instance_url + '/services/data/v57.0/graphql'
    properties = get_properties_from_model(fields, custom_fields)
    ids_url = ''
    for obj_id in obj_ids:
        ids_url += '\'' + obj_id + '\','
    ids_url = ids_url.rstrip(',')
    url_params = '?q=SELECT+' + ','.join(properties) + '+from+' + obj_type_plural + '+where+id in (' + ids_url + ')'
    url += url_params

    objects = query_object_by_ids(auth, url, obj_ids, obj_type_plural, obj_type_singular, properties, fields,
                                  custom_fields)
    if 'error' in objects:
        return {'results': [], 'error': objects['error']}

    properties_details = get_properties(auth, instance_url, obj_type_singular)

    datetime_fields = []
    if not include_field_properties:
        datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)

    for obj in objects['results']:
        if obj_type_plural == 'accounts' or obj_type_plural == 'contacts' or obj_type_plural == 'opportunities':
            if obj['data'].get('last_activity_at', None):
                get_normalized_data(obj['data'], 'last_activity_at')
            elif obj_type_plural == 'opportunities' and obj['data'].get('close_date', None):
                get_normalized_data(obj['data'], 'close_date')
        for df in datetime_fields:
            obj['data'][df] = get_normalized_datetime(obj['data'].get(df, None))

    if include_field_properties:
        properties_with_options = get_properties_with_options(auth, instance_url, obj_type_singular,
                                                              properties_details,
                                                              properties)
        fields_properties = get_fields_properties(obj_type_plural, properties_with_options, fields, custom_fields)
        for account in objects['results']:
            account['field_properties'] = copy.deepcopy(fields_properties)
            for p in account['field_properties']:
                if p['field_type'] == 'datetime':
                    account['data'][p['id']] = get_normalized_datetime(account['data'].get(p['id'], None))
                p['value'] = account['data'].get(p['id'], None)

    return objects


def execute_create_object(auth, instance_url, obj_type_singular, input_dict, fields):
    url = instance_url + "/services/data/v57.0/sobjects/" + obj_type_singular
    return upsert_object(auth, url, input_dict, fields, None)


def execute_update_object(auth, instance_url, obj_id, obj_type_singular, input_dict, fields):
    url = instance_url + "/services/data/v57.0/sobjects/" + obj_type_singular + "/" + obj_id
    return upsert_object(auth, url, input_dict, fields, obj_id)


def upsert_object(auth, url, input_dict, fields, obj_id):
    properties_dict = {}
    custom_fields = {}
    for key in input_dict:
        if key in fields:
            if isinstance(fields[key], list):
                type_field = ''
                if key == 'addresses':
                    type_field = 'address_type'
                elif key == 'email_addresses':
                    type_field = 'email_address_type'
                elif key == 'phone_numbers':
                    type_field = 'phone_number_type'

                types = []
                for fk in fields[key]:
                    params_type, text = util.get_params_value(fk[type_field], None)
                    types.append(text)

                if not isinstance(input_dict[key], list):
                    return {
                        'error': {'id': 'Bad Request', 'status_code': 400,
                                  'message': 'Invalid ' + key + ', ' + key + ' '
                                                                             'should be an array'}}

                for item in input_dict[key]:
                    if key == 'addresses':
                        street_1 = item.get('street_1', '')
                        street_2 = item.get('street_2', '')
                        full_street = street_1
                        if street_2:
                            if full_street:
                                full_street += ' '
                            full_street += street_2
                        if full_street:
                            item['street_1'] = full_street
                    try:
                        m = next(i for i in fields[key] if
                                 i[type_field].lower() == '${constant.' + item.get(type_field,
                                                                                   '').lower() + '}')
                        for it in item:
                            if it == type_field:
                                continue
                            if it in m:
                                if not m[it]:
                                    continue
                                properties_dict[m[it]] = item[it]
                            else:
                                return {
                                    'error': {'id': 'Bad Request', 'status_code': 400,
                                              'message': 'Invalid ' + key + ' property ' + it}}
                    except StopIteration:
                        return {
                            'error': {'id': 'Bad Request', 'status_code': 400,
                                      'message': 'Invalid ' + key + ', supported ' + type_field + ' : ' + ', '.join(
                                          types)}}

            else:
                properties_dict[fields[key]] = input_dict[key]
        else:
            properties_dict[key] = input_dict[key]
            custom_fields[key] = input_dict[key]
    if not obj_id:
        result = insert_object(auth, url, properties_dict)
    else:
        result = patch_object(auth, url, properties_dict, obj_id)
    if 'id' in result:
        return result
    return {'error': result['error']}


def insert_object(auth, url, properties_dict):
    request_data = properties_dict
    result = ru.post_request_with_bearer(url, auth, request_data)
    error = get_normalized_error(result)
    if not error:
        return {'id': result.json_body['id'], 'created_at': util.get_now_iso_format()}
    else:
        return error


def patch_object(auth, url, properties_dict, obj_id):
    request_data = properties_dict
    result = ru.patch_request_with_bearer(url, auth, request_data)
    error = get_normalized_error(result)
    if not error:
        return {'id': obj_id, 'updated_at': util.get_now_iso_format()}
    else:
        return error


def get_properties_from_model(common_model, custom_model):
    properties = []
    for key in common_model:
        if isinstance(common_model[key], list):
            for li in common_model[key]:
                for k in li:
                    if len(li[k]) == 0:
                        continue
                    elif '$' in li[k]:
                        properties += util.get_params_keys(li[k])

                    else:
                        properties.append(li[k])
        else:
            if len(common_model[key]) == 0:
                continue
            elif '$' in common_model[key]:
                properties += util.get_params_keys(common_model[key])
            else:
                properties.append(common_model[key])
    for field in custom_model:
        properties.append(field)
    properties = list(set(properties))
    return properties


def query_object_by_id(auth, url, obj_id, obj_type_plural, obj_type_singular, properties, common_model, custom_model):
    node_query = ''
    for p in properties:
        node_query += p + " {value} "
    query_string = f"""
    query {obj_type_plural} {{
        uiapi {{
             query {{
                 {obj_type_singular} (where: {{ Id: {{ eq: "{obj_id}" }} }}) {{
                     edges {{
                         node 
                         {{
                         Id
                         {node_query}
                         }}
                     }}
              
                 }}
             }}
        }}
    }}
    """
    result = ru.post_request_with_bearer(url, auth, {"query": query_string})

    error = get_normalized_error(result)
    if error:
        return error

    result_dict = {}
    records = result.json_body['data']['uiapi']['query'][obj_type_singular]['edges']
    if len(records) == 0:
        result_dict['error'] = {}
        result_dict['error']['id'] = 'Not found'
        result_dict['error']['status_code'] = 404
    else:
        data = {}
        for r in records[0]['node']:
            if r == 'Id':
                data['Id'] = records[0]['node']['Id']
            else:
                data[r] = records[0]['node'][r].get('value', None)
        result_dict = get_result_from_model(data, common_model, custom_model)

    return result_dict


def query_object_by_ids(auth, url, obj_ids, obj_type_plural, obj_type_singular, properties, common_model, custom_model):
    node_query = ''
    for p in properties:
        node_query += p + " {value} "
    ids_query_string = ''
    for obj_id in obj_ids:
        ids_query_string += '"' + obj_id + '",'
    ids_query_string = ids_query_string.rstrip(',')
    query_string = f"""
    query {obj_type_plural} {{
        uiapi {{
             query {{
                 {obj_type_singular} (where: {{ Id: {{ in: [ {ids_query_string} ] }} }}) {{
                     edges {{
                         node 
                         {{
                         Id
                         {node_query}
                         }}
                     }}
              
                 }}
             }}
        }}
    }}
    """
    result = ru.post_request_with_bearer(url, auth, {"query": query_string})
    error = get_normalized_error(result)
    if error:
        error['results'] = []
        return error

    data = {'results': []}
    records = result.json_body['data']['uiapi']['query'][obj_type_singular]['edges']
    for record in records:
        data_obj = {}
        for r in record['node']:
            if r == 'Id':
                data_obj['Id'] = record['node']['Id']
            else:
                data_obj[r] = record['node'][r].get('value', None)
        result_dict = get_result_from_model(data_obj, common_model, custom_model)
        data['results'].append(result_dict)
    return data


def get_result_from_model(data, common_model, custom_model):
    result = {}
    for key in common_model:
        if isinstance(common_model[key], list):
            result[key] = []
            for li in common_model[key]:
                item_dict = {}
                empty_item = True
                for k in li:
                    if len(li[k]) == 0:
                        item_dict[k] = None
                    elif '$' in li[k]:
                        params_type, item_dict[k] = util.get_params_value(li[k], data)
                        if item_dict[k] and not params_type == 'constant':
                            empty_item = False
                    elif li[k] in data:
                        item_dict[k] = data.get(li[k], None)
                        if item_dict[k]:
                            empty_item = False
                if not empty_item:
                    result[key].append(item_dict)
        elif len(common_model[key]) == 0:
            result[key] = None
        elif '$' in common_model[key]:
            params_type, result[key] = util.get_params_value(common_model[key], data)
        elif common_model[key] in data:
            result[key] = data.get(common_model[key], None)
    if custom_model:
        for key in custom_model:
            if key in data:
                result[key] = data[key]

    return {'id': data.get('Id', None), 'data': result}


def get_normalized_data(data, key):
    if not data.get(key, None):
        return None
    match key:
        case 'last_activity_at':
            data[key] = data[key] + 'T00:00:00Z'
        case 'close_date':
            data[key] = data[key] + 'T00:00:00Z'
        case _:
            return data[key]
    return data[key]


def get_normalized_datetime(salesforce_datetime):
    if not salesforce_datetime:
        return None
    date_parts = salesforce_datetime.split('.')
    if len(date_parts) == 2:
        return date_parts[0] + 'Z'
    return salesforce_datetime


def get_datetime_fields(properties, common_models, custom_model):
    datetime_properties = [x['QualifiedApiName'] for x in properties if x['DataType'] == 'Date/Time']
    fields = util.merge_model(common_models, custom_model)
    datetime_fields = []
    for key in fields:
        if isinstance(fields[key], list):
            continue
        original_key_name = key
        if key in common_models:
            original_key_name = fields[key]
        if original_key_name in datetime_properties:
            datetime_fields.append(key)
    return datetime_fields


def get_properties(auth, instance_url, obj_type):
    url = instance_url + "/services/data/v57.0/query/"
    url_params = '?q=Select Label, DataType, QualifiedApiName, Description, IsNillable from FieldDefinition where EntityDefinition.QualifiedApiName = \'' + obj_type + '\''
    url += url_params
    result = ru.get_request_with_bearer(url, auth)
    records = []
    if result.success:
        records = result.json_body.get('records', [])
    return records


def get_properties_with_options(auth, instance_url, obj_type, records, fields):
    for r in records:
        data_type = r['DataType'].lower()
        field_name = r['QualifiedApiName']
        if field_name in fields:
            if data_type == 'picklist (multi-select)' or data_type == 'picklist':
                r['field_choices'] = get_picklist(auth, instance_url, obj_type, field_name)

    return records


def get_fields_properties(obj_type, properties, common_models, custom_model):
    field_properties = []
    fields = util.merge_model(common_models, custom_model)
    for key in fields:
        if isinstance(fields[key], list):
            continue
        original_key_name = key
        is_custom = True
        if key in common_models:
            original_key_name = fields[key]
            is_custom = False
        try:
            property_obj = next(i for i in properties if i['QualifiedApiName'] == original_key_name)
            field_obj = {'id': key, 'display_name': property_obj['Label'], 'origin_key_name': original_key_name,
                         'description': property_obj['Description'], 'is_custom': is_custom}
            data_type = property_obj['DataType']
            field_type, field_format = get_normalized_field_type(data_type)
            field_obj['field_type'] = field_type
            field_obj['field_format'] = field_format
            field_obj['is_required'] = not property_obj['IsNillable']
            if 'field_choices' in property_obj:
                field_obj['field_choices'] = property_obj['field_choices']

            if obj_type == 'accounts' or obj_type == 'contacts' or obj_type == 'opportunities':
                if key == 'last_activity_at':
                    field_obj['field_type'] = 'datetime'
                elif obj_type == 'opportunities':
                    if key == 'close_date':
                        field_obj['field_type'] = 'datetime'
                    elif key == 'stage_id':
                        field_obj['field_type'] = 'text'
                        field_obj['field_choices'] = []

            field_properties.append(field_obj)

        except StopIteration:
            if obj_type == 'opportunities':
                if key == 'status':
                    field_obj = {'id': key, 'display_name': 'Status', 'origin_key_name': None,
                                 'description': 'Deal WON/LOST status',
                                 'is_custom': False, 'field_type': 'select',
                                 'field_choices': [{'label': 'OPEN', 'value': 'OPEN'}, {'label': 'WON', 'value': 'WON'},
                                                   {'label': 'LOST', 'value': 'LOST'}], 'field_format': '',
                                 'is_required': False}
                    field_properties.append(field_obj)
            elif obj_type == 'stages':
                if key == 'name':
                    field_obj = {'id': key, 'display_name': 'Name', 'origin_key_name': None,
                                 'description': 'Pipeline deal stage name',
                                 'is_custom': False, 'field_type': 'text', 'field_choices': [], 'field_format': '',
                                 'is_required': False}
                    field_properties.append(field_obj)

    return field_properties


def get_normalized_field_type(field_type):
    field_format = field_type.lower()

    if 'Multi-Select' in field_type:
        return 'multiselect', field_format
    elif 'Text Area' in field_type:
        return 'textarea', field_format

    type_parts = field_type.split('(')
    match type_parts[0]:
        case 'Name' | 'URL' | 'Lookup' | 'Text' | 'External Lookup' | 'Hierarchy' | 'Phone' | 'Fax' | 'Email' | 'Formula' | 'Roll-Up Summary':
            field_type = 'text';
        case 'Currency':
            field_type = 'number'
            field_format = 'currency'
        case 'Percent':
            field_type = 'number'
            field_format = 'percentage'
        case 'Number' | 'Auto Number':
            field_type = 'number'
        case 'Long Text Area':
            field_type = 'textarea'
        case 'Date/Time':
            field_type = 'datetime'
            field_format = 'datetime'
        case 'Date':
            field_type = 'date'
            field_format = 'date'
        case 'Time':
            field_type = 'time'
        case 'Checkbox':
            field_type = 'boolean'
        case 'Picklist':
            field_type = 'select'
        case _:
            return field_type.lower(), field_type.lower()
    return field_type, field_format


def get_picklist(auth, instance_url, obj_type, field_name):
    field_choices = []
    url = instance_url + '/services/data/v57.0/ui-api/object-info/' + obj_type + '/picklist-values/012000000000000AAA/' + field_name
    result = ru.get_request_with_bearer(url, auth)
    if result.success:
        options = result.json_body['values']
        for opt in options:
            field_choices.append({'label': opt['label'], 'value': opt['value']})
    return field_choices


def query_objects(auth, url, obj_type_plural, obj_type_singular, properties, common_model, custom_model, owner_id,
                  created_before,
                  created_after, modified_before, modified_after, limit, cursor):
    node_query = ''
    for p in properties:
        node_query += p + " {value} "

    limit_query = 'first : ' + str(limit)
    if cursor:
        limit_query += ', after : "' + cursor + '"'
    else:
        limit_query += ', after : null'
    if owner_id:
        limit_query += ' where: { OwnerId: { eq: "' + owner_id + '" } }'
    elif created_before:
        limit_query += ' where: { CreatedDate: { lt: {value: "' + created_before + '"} } }'
    elif created_after:
        limit_query += ' where: { CreatedDate: { gte: {value: "' + created_after + '"} } }'
    elif modified_before:
        limit_query += ' where: { LastModifiedDate: { lt: {value: "' + modified_before + '"} } }'
    elif modified_after:
        limit_query += ' where: { LastModifiedDate: { gte: {value: "' + modified_after + '"} } }'

    if limit_query:
        limit_query = '(' + limit_query + ')'

    query_string = f"""
    query {obj_type_plural} {{
        uiapi {{
             query {{
                 {obj_type_singular} {limit_query} {{
                     edges {{
                         node 
                         {{
                         Id
                         {node_query}
                         }}
                     }}
                     totalCount
            pageInfo {{
              startCursor
              endCursor
              hasNextPage
              hasPreviousPage
            }}
                 }}
             }}
        }}
    }}
    """

    result = ru.post_request_with_bearer(url, auth, {"query": query_string})
    error = get_normalized_error(result)
    if error:
        error['results'] = []
        return error

    data = {'results': []}

    records = result.json_body['data']['uiapi']['query'][obj_type_singular]['edges']

    for record in records:
        data_obj = {}
        for r in record['node']:
            if r == 'Id':
                data_obj['Id'] = record['node']['Id']
            else:
                data_obj[r] = record['node'][r].get('value', None)
        result_dict = get_result_from_model(data_obj, common_model, custom_model)
        data['results'].append(result_dict)

    page_info = result.json_body['data']['uiapi']['query'][obj_type_singular]['pageInfo']

    next_cursor = page_info.get('endCursor', None)
    has_next_page = page_info.get('hasNextPage', False)
    if next_cursor and has_next_page:
        data['next_cursor'] = next_cursor

    return data


def capitalize_first_letter(text):
    if not text:
        return None
    if len(text) == 1:
        return text.upper()
    return text[:1].upper() + text[1:]


def get_normalized_error(response):
    error_data = {}
    if response.json_body and 'errors' in response.json_body and isinstance(response.json_body['errors'], list) and len(
            response.json_body['errors']) > 0:
        error_data['error'] = {}
        error_data['error']['id'] = 'Bad request'
        error_data['error']['status_code'] = 400
        error = ''
        for e in response.json_body['errors']:
            error += e.get('message', '') + ' '
        error_data['error']['message'] = error.rstrip(' ')
        return error_data
    elif not response.success:
        error_data['error'] = {}
        error_data['error']['id'] = response.error_description
        error_data['error']['status_code'] = response.status_code
        if isinstance(response.json_body, list):
            error = ''
            for e in response.json_body:
                error += e.get('message', '') + ' '
            error_data['error']['message'] = error.rstrip(' ')
        elif response.json_body:
            error_data['error']['message'] = response.json_body.get('message', response.json_body)
        return error_data


def convert_datetime_to_date(datetime_string):
    if not datetime_string:
        return
    try:
        utc_dt = datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%SZ').date()
        return utc_dt.strftime('%Y-%m-%d')
    except ValueError:
        return None


def get_stage_by_id(auth, instance_url, obj_id, fields, include_field_properties):
    records = get_stage_objects(auth, instance_url, [obj_id], fields)
    result_dict = {'id': obj_id}
    if 'error' in records:
        return {'id': obj_id, 'error': records['error']}
    elif len(records['results']) == 0:
        result_dict['error'] = {}
        result_dict['error']['id'] = 'Not found'
        result_dict['error']['status_code'] = 404
        return result_dict

    result_dict['data'] = records['results'][0]['data']
    if include_field_properties:
        result_dict['field_properties'] = get_stage_properties('stages', fields, result_dict['data'])
    return result_dict


def get_stages(auth, instance_url, obj_ids, fields, include_field_properties):
    results = get_stage_objects(auth, instance_url, obj_ids, fields)
    if 'error' in results:
        return results

    if include_field_properties:
        for r in results['results']:
            r['field_properties'] = get_stage_properties('stages', fields, r['data'])

    return results


def get_stage_objects(auth, instance_url, obj_ids, fields):
    url = instance_url + '/services/data/v57.0/ui-api/object-info/Opportunity/picklist-values/012000000000000AAA/StageName'
    result = ru.get_request_with_bearer(url, auth)
    records = []
    error = get_normalized_error(result)
    if not error:
        options = result.json_body['values']
        for opt in options:
            if len(obj_ids) > 0:
                if opt['value'] in obj_ids:
                    obj = {'id': opt['value'], 'data': {'name': opt[fields['name']]}}
                    records.append(obj)
            else:
                obj = {'id': opt['value'], 'data': {'name': opt[fields['name']]}}
                records.append(obj)
        return {'results': records}
    else:
        error['results'] = []
        return error


def get_stage_properties(obj_type, fields, values):
    properties = []
    field_properties = get_fields_properties(obj_type, properties, fields, None)
    for p in field_properties:
        p['value'] = values.get(p['id'], None)
    return field_properties


def execute_get_field_properties(auth, instance_url, obj_type_plural, obj_type_singular, fields):
    if obj_type_plural == 'stages':
        properties = []
        properties_details = []
    else:
        properties = get_properties_from_model(fields, [])
        properties_details = get_properties(auth, instance_url, obj_type_singular)

    properties_with_options = get_properties_with_options(auth, instance_url, obj_type_singular,
                                                          properties_details,
                                                          properties)
    fields_properties = get_fields_properties(obj_type_plural, properties_with_options, fields, [])

    return {'results': fields_properties}
