import json
import integrations.connectors.connectors_utils as util
import dive.api.request_utils as ru
from pathlib import Path
import copy


def get_object_by_id(auth, app, obj_type, obj_id, include_field_properties, custom_fields):
    base_path = Path(__file__).parent
    try:
        with open(str(base_path) + '/' + obj_type + '.json') as f:
            field_dict = json.load(f)
    except FileNotFoundError:
        return

    config = json.loads(app.auth_json)
    instance_url = config.get('instance_url', None)
    match obj_type:
        case 'accounts':
            return get_account_by_id(auth, instance_url, obj_id, 'accounts', field_dict, custom_fields,
                                     include_field_properties)
        case _:
            return


def get_objects(auth, app, obj_type, include_field_properties, custom_fields, obj_ids: [], owner_id, created_before,
                created_after, modified_before, modified_after, page_size, cursor):
    base_path = Path(__file__).parent
    try:
        with open(str(base_path) + '/' + obj_type + '.json') as f:
            field_dict = json.load(f)
    except FileNotFoundError:
        return

    config = json.loads(app.auth_json)
    instance_url = config.get('instance_url', None)

    if len(obj_ids) > 0:
        match obj_type:
            case 'accounts':
                return get_accounts_by_ids(auth, instance_url, obj_ids, 'accounts', field_dict, custom_fields,
                                           include_field_properties)
            case _:
                return
    else:
        match obj_type:

            case 'accounts':
                return get_accounts(auth, instance_url, 'accounts', field_dict, custom_fields, include_field_properties,
                                    owner_id,
                                    created_before, created_after, modified_before, modified_after,
                                    page_size, cursor)
            case _:
                return


def get_account_by_id(auth, instance_url, obj_id, obj_type, fields, custom_fields, include_field_properties):
    obj_type_singular = capitalize_first_letter(obj_type[:-1])
    url = instance_url + '/services/data/v57.0/graphql'
    properties = get_properties_from_model(fields, custom_fields)
    account = query_object_by_id(auth, url, obj_id, obj_type, obj_type_singular, properties, fields, custom_fields)
    result = {'id': obj_id}
    properties_details = get_properties(auth, instance_url, obj_type_singular)
    if 'data' in account:
        if account['data'].get('last_activity_at', None):
            get_normalized_data(account['data'], 'last_activity_at')
        if not include_field_properties:
            datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)
            for df in datetime_fields:
                account['data'][df] = get_normalized_datetime(account['data'].get(df, None))
            result['data'] = account['data']
        elif include_field_properties:
            properties_with_options = get_properties_with_options(auth, instance_url, obj_type_singular,
                                                                  properties_details,
                                                                  properties)
            fields_properties = get_fields_properties(properties_with_options, fields, custom_fields)
            for p in fields_properties:
                if p['field_type'] == 'datetime':
                    account['data'][p['id']] = get_normalized_datetime(account['data'].get(p['id'], None))
                p['value'] = account['data'].get(p['id'], None)
            result['data'] = account['data']
            result['field_properties'] = fields_properties
    elif 'error' in account:
        result['error'] = account['error']
    return result


def get_accounts(auth, instance_url, obj_type, fields, custom_fields, include_field_properties, owner_id,
                 created_before,
                 created_after, modified_before, modified_after, limit, cursor):
    properties = get_properties_from_model(fields, custom_fields)
    obj_type_singular = capitalize_first_letter(obj_type[:-1])
    if not limit:
        limit = '100'
    url = instance_url + '/services/data/v57.0/graphql'
    accounts = query_objects(auth, url, obj_type, obj_type_singular, properties, fields, custom_fields, owner_id,
                             created_before,
                             created_after, modified_before, modified_after, limit, cursor)
    if 'error' in accounts:
        return {'results': [], 'error': accounts['error']}

    properties_details = get_properties(auth, instance_url, obj_type_singular)

    datetime_fields = []
    if not include_field_properties:
        datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)

    for account in accounts['results']:
        if account['data'].get('last_activity_at', None):
            get_normalized_data(account['data'], 'last_activity_at')
        for df in datetime_fields:
            account['data'][df] = get_normalized_datetime(account['data'].get(df, None))

    if include_field_properties:
        properties_with_options = get_properties_with_options(auth, instance_url, obj_type_singular,
                                                              properties_details,
                                                              properties)
        fields_properties = get_fields_properties(properties_with_options, fields, custom_fields)
        for account in accounts['results']:
            account['field_properties'] = copy.deepcopy(fields_properties)
            for p in account['field_properties']:
                if p['field_type'] == 'datetime':
                    account['data'][p['id']] = get_normalized_datetime(account['data'].get(p['id'], None))
                p['value'] = account['data'].get(p['id'], None)

    return accounts


def get_accounts_by_ids(auth, instance_url, obj_ids: [], obj_type, fields, custom_fields, include_field_properties):
    obj_type_singular = capitalize_first_letter(obj_type[:-1])
    url = instance_url + '/services/data/v57.0/graphql'
    properties = get_properties_from_model(fields, custom_fields)
    ids_url = ''
    for obj_id in obj_ids:
        ids_url += '\'' + obj_id + '\','
    ids_url = ids_url.rstrip(',')
    url_params = '?q=SELECT+' + ','.join(properties) + '+from+' + obj_type + '+where+id in (' + ids_url + ')'
    url += url_params

    accounts = query_object_by_ids(auth, url, obj_ids, obj_type, obj_type_singular, properties, fields, custom_fields)
    if 'error' in accounts:
        return {'results': [], 'error': accounts['error']}

    properties_details = get_properties(auth, instance_url, obj_type_singular)

    datetime_fields = []
    if not include_field_properties:
        datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)

    for account in accounts['results']:
        if account['data'].get('last_activity_at', None):
            get_normalized_data(account['data'], 'last_activity_at')
        for df in datetime_fields:
            account['data'][df] = get_normalized_datetime(account['data'].get(df, None))

    if include_field_properties:
        properties_with_options = get_properties_with_options(auth, instance_url, obj_type_singular,
                                                              properties_details,
                                                              properties)
        fields_properties = get_fields_properties(properties_with_options, fields, custom_fields)
        for account in accounts['results']:
            account['field_properties'] = copy.deepcopy(fields_properties)
            for p in account['field_properties']:
                if p['field_type'] == 'datetime':
                    account['data'][p['id']] = get_normalized_datetime(account['data'].get(p['id'], None))
                p['value'] = account['data'].get(p['id'], None)

    return accounts


def get_properties_from_model(common_model, custom_model):
    properties = []
    for key in common_model:
        if isinstance(common_model[key], list):
            for li in common_model[key]:
                for k in li:
                    if len(li[k]) == 0:
                        continue
                    elif li[k][0] == '$':
                        properties += util.get_params_keys(li[k])

                    else:
                        properties.append(li[k])
        else:
            if len(common_model[key]) == 0:
                continue
            elif common_model[key][0] == '$':
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
    result_dict = {}
    if result.success:
        if 'errors' in result.json_body and len(result.json_body['errors']) > 0:
            result_dict['error'] = {}
            result_dict['error']['id'] = 'Bad request'
            result_dict['error']['status_code'] = 400
            error = ''
            for e in result.json_body['errors']:
                error += e.get('message', '') + ' '
            result_dict['error']['message'] = error.rstrip(' ')
            return result_dict

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
    else:
        result_dict['error'] = {}
        result_dict['error']['id'] = result.error_description
        result_dict['error']['status_code'] = result.status_code
        if isinstance(result.json_body, list):
            error = ''
            for e in result.json_body:
                error += e.get('message', '') + ' '
            result_dict['error']['message'] = error.rstrip(' ')
        else:
            result_dict['error']['message'] = result.json_body.get('message', result.json_body)

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
    data = {'results': []}
    if result.success:
        if 'errors' in result.json_body and len(result.json_body['errors']) > 0:
            data['error'] = {}
            data['error']['id'] = 'Bad request'
            data['error']['status_code'] = 400
            error = ''
            for e in result.json_body['errors']:
                error += e.get('message', '') + ' '
            data['error']['message'] = error.rstrip(' ')
            return data

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

    else:
        data['error'] = {}
        data['error']['id'] = result.error_description
        data['error']['status_code'] = result.status_code
        if result.json_body:
            if isinstance(result.json_body, list):
                error = ''
                for e in result.json_body:
                    error += e.get('message', '') + ' '
                data['error']['message'] = error.rstrip(' ')
            else:
                data['error']['message'] = result.json_body.get('message', result.json_body)

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
                    elif li[k][0] == '$':
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
        elif common_model[key][0] == '$':
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
    url_params = '?q=Select Label, DataType, QualifiedApiName, Description from FieldDefinition where EntityDefinition.QualifiedApiName = \'' + obj_type + '\''
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


def get_fields_properties(properties, common_models, custom_model):
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
            if 'field_choices' in property_obj:
                field_obj['field_choices'] = property_obj['field_choices']
            field_properties.append(field_obj)

        except StopIteration:
            continue
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
    limit_query = 'first : ' + limit
    if cursor:
        limit_query += ', after : "' + cursor + '"'
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
    query_string = f"""
    query {obj_type_plural} {{
        uiapi {{
             query {{
                 {obj_type_singular} ({limit_query}) {{
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
    data = {'results': []}
    if result.success:
        if 'errors' in result.json_body and len(result.json_body['errors']) > 0:
            data['error'] = {}
            data['error']['id'] = 'Bad request'
            data['error']['status_code'] = 400
            error = ''
            for e in result.json_body['errors']:
                error += e.get('message', '') + ' '
            data['error']['message'] = error.rstrip(' ')
            return data
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
    else:
        data['error'] = {}
        data['error']['id'] = result.error_description
        data['error']['status_code'] = result.status_code
        if result.json_body:
            if isinstance(result.json_body, list):
                error = ''
                for e in result.json_body:
                    error += e.get('message', '') + ' '
                data['error']['message'] = error.rstrip(' ')
            else:
                data['error']['message'] = result.json_body.get('message', result.json_body)

    return data


def capitalize_first_letter(text):
    if not text:
        return None
    if len(text) == 1:
        return text.upper()
    return text[:1].upper() + text[1:]
