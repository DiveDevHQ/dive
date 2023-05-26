import integrations.connectors.connectors_utils as util
import dive.api.request_utils as ru
from datetime import datetime
from urllib.parse import urlparse
import json
import copy
from pathlib import Path


def get_object_by_id(auth, app, obj_type, obj_id, include_field_properties, custom_fields):
    base_path = Path(__file__).parent
    try:
        with open(str(base_path) + '/' + obj_type + '.json') as f:
            field_dict = json.load(f)
    except FileNotFoundError:
        return

    match obj_type:
        case 'contacts':
            return get_contact_by_id(auth, obj_id, field_dict, custom_fields, include_field_properties)
        case 'accounts':
            return get_company_by_id(auth, obj_id, field_dict, custom_fields, include_field_properties)
        case 'opportunities':
            return get_deal_by_id(auth, obj_id, field_dict, custom_fields, include_field_properties)
        case 'stages':
            return get_stage_by_id(auth, obj_id, field_dict, include_field_properties)
        case 'users':
            return get_owner_by_id(auth, obj_id, field_dict, include_field_properties)
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

    if len(obj_ids) > 0:
        match obj_type:
            case 'contacts':
                return get_contacts_by_ids(auth, obj_ids, field_dict, custom_fields, include_field_properties)
            case 'accounts':
                return get_companies_by_ids(auth, obj_ids, field_dict, custom_fields, include_field_properties)
            case 'opportunities':
                return get_deals_by_ids(auth, obj_ids, field_dict, custom_fields, include_field_properties)
            case 'stages':
                return get_stages(auth, obj_ids, field_dict, include_field_properties,
                                  None, None, None, None)
            case 'users':
                return get_owners(auth, obj_ids, field_dict, include_field_properties,
                                  None, None, None, None)
            case _:
                return
    else:
        if created_before:
            created_before = convert_iso_date_to_timestamp(created_before)
        if created_after:
            created_after = convert_iso_date_to_timestamp(created_after)
        if modified_before:
            modified_before = convert_iso_date_to_timestamp(modified_before)
        if modified_after:
            modified_after = convert_iso_date_to_timestamp(modified_after)
        match obj_type:
            case 'contacts':
                return get_contacts_by_filter(auth, field_dict, custom_fields, include_field_properties, owner_id,
                                              created_before, created_after, modified_before, modified_after,
                                              page_size, cursor)
            case 'accounts':
                return get_companies_by_filter(auth, field_dict, custom_fields, include_field_properties, owner_id,
                                               created_before, created_after, modified_before, modified_after,
                                               page_size, cursor)
            case 'opportunities':
                return get_deals_by_filter(auth, field_dict, custom_fields, include_field_properties, owner_id,
                                           created_before, created_after, modified_before, modified_after,
                                           page_size, cursor)
            case 'stages':
                return get_stages(auth, [], field_dict, include_field_properties,
                                  created_before, created_after, modified_before, modified_after)
            case 'users':
                return get_owners(auth, [], field_dict, include_field_properties,
                                  created_before, created_after, modified_before, modified_after)
            case _:
                return


def create_object(auth, app, obj_type, input_data):
    base_path = Path(__file__).parent
    try:
        with open(str(base_path) + '/' + obj_type + '.json') as f:
            field_dict = json.load(f)
    except FileNotFoundError:
        return

    match obj_type:
        case 'accounts':
            return create_company(auth, input_data, field_dict)
        case 'contacts':
            return create_contact(auth, input_data, field_dict)
        case 'opportunities':
            return create_deal(auth, input_data, field_dict)
        case _:
            return


def update_object(auth, app, obj_id, obj_type, input_data):
    base_path = Path(__file__).parent
    try:
        with open(str(base_path) + '/' + obj_type + '.json') as f:
            field_dict = json.load(f)
    except FileNotFoundError:
        return

    match obj_type:
        case 'accounts':
            return update_company(auth, obj_id, input_data, field_dict)
        case 'contacts':
            return update_contact(auth, obj_id, input_data, field_dict)
        case 'opportunities':
            return update_deal(auth, obj_id, input_data, field_dict)
        case _:
            return


def get_contact_by_id(auth, obj_id, fields, custom_fields, include_field_properties):
    url = "https://api.hubapi.com/crm/v3/objects/contacts/" + str(obj_id)
    properties = get_properties_from_model(fields, custom_fields)
    url_params = ''
    for p in properties:
        url_params += '&properties=' + p
    url += '?' + url_params
    contact = query_object_by_id(auth, url, fields, custom_fields)
    result = {'id': obj_id}
    url_properties = "https://api.hubapi.com/properties/v1/contacts/properties"
    properties_details = get_properties(auth, url_properties)

    if 'data' in contact:
        if not include_field_properties:
            datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)
            for df in datetime_fields:
                contact['data'][df] = get_normalized_datetime(contact['data'].get(df, None))
    elif 'error' in contact:
        result['error'] = contact['error']
        return result

    field_properties = None
    if include_field_properties and 'data' in contact:
        field_properties = get_fields_properties(properties_details, fields, custom_fields)
        for p in field_properties:
            if p['field_type'] == 'datetime':
                contact['data'][p['id']] = get_normalized_datetime(contact['data'].get(p['id'], None))
            p['value'] = contact['data'].get(p['id'], None)

    if 'data' in contact:
        result['data'] = contact['data']
    if field_properties:
        result['field_properties'] = field_properties

    return result


def get_contacts_by_ids(auth, obj_ids: [], fields, custom_fields, include_field_properties):
    url = "https://api.hubapi.com/crm/v3/objects/contacts/batch/read"
    properties = get_properties_from_model(fields, custom_fields)

    data = query_objects_by_ids_batch(auth, url, obj_ids, properties, fields, custom_fields)
    contacts = data['results']
    url_properties = "https://api.hubapi.com/properties/v1/contacts/properties"
    properties_details = get_properties(auth, url_properties)
    datetime_fields = []

    if not include_field_properties:
        datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)

    for contact in contacts:
        for df in datetime_fields:
            contact['data'][df] = get_normalized_datetime(contact['data'].get(df, None))

    if include_field_properties:
        field_properties = get_fields_properties(properties_details, fields, custom_fields)
        for contact in contacts:
            contact['field_properties'] = copy.deepcopy(field_properties)
            for p in contact['field_properties']:
                if p['field_type'] == 'datetime':
                    contact['data'][p['id']] = get_normalized_datetime(contact['data'].get(p['id'], None))
                p['value'] = contact['data'].get(p['id'], None)

    if 'error' in data:
        return {'results': contacts, 'error': data['error']}
    else:
        return {'results': contacts}


def get_company_by_id(auth, obj_id, fields, custom_fields, include_field_properties):
    url = "https://api.hubapi.com/crm/v3/objects/companies/" + str(obj_id)
    url_params = ''
    properties = get_properties_from_model(fields, custom_fields)
    for p in properties:
        url_params += '&properties=' + p
    url += '?' + url_params
    company = query_object_by_id(auth, url, fields, custom_fields)
    result = {'id': obj_id}

    url_properties = "https://api.hubapi.com/properties/v1/companies/properties"
    properties_details = get_properties(auth, url_properties)
    if 'data' in company:
        if not include_field_properties:
            datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)
            for df in datetime_fields:
                company['data'][df] = get_normalized_datetime(company['data'].get(df, None))
    elif 'error' in company:
        result['error'] = company['error']
        return result

    field_properties = None
    if include_field_properties and 'data' in company:
        field_properties = get_fields_properties(properties_details, fields, custom_fields)
        for p in field_properties:
            if p['field_type'] == 'datetime':
                company['data'][p['id']] = get_normalized_datetime(company['data'].get(p['id'], None))
            p['value'] = company['data'].get(p['id'], None)

    if 'data' in company:
        result['data'] = company['data']
    if field_properties:
        result['field_properties'] = field_properties

    return result


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


def get_companies_by_ids(auth, obj_ids: [], fields, custom_fields, include_field_properties):
    url = "https://api.hubapi.com/crm/v3/objects/companies/batch/read"
    properties = get_properties_from_model(fields, custom_fields)
    data = query_objects_by_ids_batch(auth, url, obj_ids, properties, fields, custom_fields)
    companies = data['results']

    url_properties = "https://api.hubapi.com/properties/v1/companies/properties"
    properties_details = get_properties(auth, url_properties)

    datetime_fields = []
    if not include_field_properties:
        datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)

    for company in companies:
        for df in datetime_fields:
            company['data'][df] = get_normalized_datetime(company['data'].get(df, None))

    if include_field_properties:
        field_properties = get_fields_properties(properties_details, fields, custom_fields)
        for company in companies:
            company['field_properties'] = copy.deepcopy(field_properties)
            for p in company['field_properties']:
                if p['field_type'] == 'datetime':
                    company['data'][p['id']] = get_normalized_datetime(company['data'].get(p['id'], None))
                p['value'] = company['data'].get(p['id'], None)

    if 'error' in data:
        return {'results': companies, 'error': data['error']}
    else:
        return {'results': companies}


def get_deals_by_ids(auth, object_ids: [], fields, custom_fields, include_field_properties):
    url = "https://api.hubapi.com/crm/v3/objects/deals/batch/read"
    properties = get_properties_from_model(fields, custom_fields)
    data = query_objects_by_ids_batch(auth, url, object_ids, properties, fields, custom_fields)
    deals = data['results']

    association_url = "https://api.hubapi.com/crm/v3/associations/deal/company/batch/read"
    associations = query_associations_by_ids_batch(auth, association_url, object_ids)

    url_properties = "https://api.hubapi.com/properties/v1/deals/properties"
    properties_details = get_properties(auth, url_properties)

    datetime_fields = []
    if not include_field_properties:
        datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)

    for deal in deals:
        for df in datetime_fields:
            deal['data'][df] = get_normalized_datetime(deal['data'].get(df, None))
        try:
            m = next(i for i in associations['results'] if
                     str(i['id']) == str(deal['id']))
            if len(m['associated_ids']) > 0:
                deal['data']['account_id'] = m['associated_ids'][0]
        except StopIteration:
            continue

    if include_field_properties:
        field_properties = get_fields_properties(properties_details, fields, custom_fields)
        for deal in deals:
            deal['field_properties'] = copy.deepcopy(field_properties)
            for p in deal['field_properties']:
                if p['field_type'] == 'datetime':
                    deal['data'][p['id']] = get_normalized_datetime(deal['data'].get(p['id'], None))
                p['value'] = deal['data'].get(p['id'], None)

    if 'error' in data:
        return {'results': deals, 'error': data['error']}
    else:
        return {'results': deals}


def get_contacts_by_filter(auth, fields, custom_fields, include_field_properties, owner_id, created_before,
                           created_after, modified_before, modified_after, limit, cursor):
    url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
    properties = get_properties_from_model(fields, custom_fields)

    filters = []
    if owner_id:
        f = {'filter_field': fields['owner_id'], 'filter_operator': 'EQ', 'filter_value': owner_id}
        filters.append(f)
    elif created_before:
        f = {'filter_field': 'createdate', 'filter_operator': 'LT', 'filter_value': int(created_before)}
        filters.append(f)
    elif created_after:
        f = {'filter_field': 'createdate', 'filter_operator': 'GTE', 'filter_value': int(created_after)}
        filters.append(f)
    elif modified_before:
        f = {'filter_field': 'lastmodifieddate', 'filter_operator': 'LT',
             'filter_value': int(modified_before)}
        filters.append(f)
    elif modified_after:
        f = {'filter_field': 'lastmodifieddate', 'filter_operator': 'GTE',
             'filter_value': int(modified_after)}
        filters.append(f)
    if not limit:
        limit = '100'
    data = query_objects_by_filter(auth, url, properties, fields, custom_fields, filters, limit, cursor)
    contacts = data['results']

    url_properties = "https://api.hubapi.com/properties/v1/contacts/properties"
    properties_details = get_properties(auth, url_properties)
    datetime_fields = []
    if not include_field_properties:
        datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)

    for contact in contacts:
        for df in datetime_fields:
            contact['data'][df] = get_normalized_datetime(contact['data'].get(df, None))

    if include_field_properties:
        field_properties = get_fields_properties(properties_details, fields, custom_fields)
        for contact in contacts:
            contact['field_properties'] = copy.deepcopy(field_properties)
            for p in contact['field_properties']:
                if p['field_type'] == 'datetime':
                    contact['data'][p['id']] = get_normalized_datetime(contact['data'].get(p['id'], None))
                p['value'] = contact['data'].get(p['id'], None)

    result = {'results': contacts}
    if 'error' in data:
        result['error'] = data['error']
    if 'next_cursor' in data:
        result['next_cursor'] = data['next_cursor']
    return result


def get_companies_by_filter(auth, fields, custom_fields, include_field_properties, owner_id, created_before,
                            created_after, modified_before, modified_after, limit, cursor):
    url = "https://api.hubapi.com/crm/v3/objects/companies/search"
    properties = get_properties_from_model(fields, custom_fields)

    filters = []
    if owner_id:
        f = {'filter_field': 'hubspot_owner_id', 'filter_operator': 'EQ', 'filter_value': owner_id}
        filters.append(f)
    elif created_before:
        f = {'filter_field': 'createdate', 'filter_operator': 'LT', 'filter_value': int(created_before)}
        filters.append(f)
    elif created_after:
        f = {'filter_field': 'createdate', 'filter_operator': 'GTE', 'filter_value': int(created_after)}
        filters.append(f)
    elif modified_before:
        f = {'filter_field': 'hs_lastmodifieddate', 'filter_operator': 'LT',
             'filter_value': int(modified_before)}
        filters.append(f)
    elif modified_after:
        f = {'filter_field': 'hs_lastmodifieddate', 'filter_operator': 'GTE',
             'filter_value': int(modified_after)}
        filters.append(f)
    if not limit:
        limit = '100'
    data = query_objects_by_filter(auth, url, properties, fields, custom_fields, filters, limit, cursor)
    companies = data['results']

    url_properties = "https://api.hubapi.com/properties/v1/contacts/properties"
    properties_details = get_properties(auth, url_properties)
    datetime_fields = []
    if not include_field_properties:
        datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)

    for company in companies:
        for df in datetime_fields:
            company['data'][df] = get_normalized_datetime(company['data'].get(df, None))

    if include_field_properties:
        field_properties = get_fields_properties(properties_details, fields, custom_fields)
        for company in companies:
            company['field_properties'] = copy.deepcopy(field_properties)
            for p in company['field_properties']:
                if p['field_type'] == 'datetime':
                    company['data'][p['id']] = get_normalized_datetime(company['data'].get(p['id'], None))
                p['value'] = company['data'].get(p['id'], None)

    result = {'results': companies}
    if 'error' in data:
        result['error'] = data['error']
    if 'next_cursor' in data:
        result['next_cursor'] = data['next_cursor']
    return result


def create_company(auth, input_dict, fields):
    url = "https://api.hubapi.com/crm/v3/objects/companies"
    return upsert_company(auth, url, input_dict, fields, None)


def update_company(auth, obj_id, input_dict, fields):
    url = "https://api.hubapi.com/crm/v3/objects/companies/" + obj_id
    return upsert_company(auth, url, input_dict, fields, obj_id)


def upsert_company(auth, url, input_dict, fields, obj_id):
    properties_dict = {}
    custom_fields = {}
    for key in input_dict:
        if key in fields:
            if key == 'website':
                domain = urlparse(input_dict[key]).netloc
                properties_dict['domain'] = domain or input_dict[key]
                properties_dict[fields[key]] = input_dict[key]
            elif key == 'addresses':
                type_field = 'address_type'
                address_types = []
                for fk in fields[key]:
                    params_type, text = util.get_params_value(fk[type_field], None)
                    address_types.append(text)

                if not isinstance(input_dict[key], list):
                    return {
                        'error': {'id': 'Bad Request', 'status_code': 400, 'message': 'Invalid addresses, addresses '
                                                                                      'should be an array'}}
                for address in input_dict[key]:
                    try:
                        m = next(i for i in fields[key] if
                                 i[type_field].lower() == '${constant.' + address.get(type_field,
                                                                                      '').lower() + '}')
                        for a in address:
                            if a == type_field:
                                continue
                            if a in m:
                                if not m[a]:
                                    continue
                                properties_dict[m[a]] = address[a]
                            else:
                                return {
                                    'error': {'id': 'Bad Request', 'status_code': 400,
                                              'message': 'Invalid addresses property ' + a}}
                    except StopIteration:
                        return {
                            'error': {'id': 'Bad Request', 'status_code': 400,
                                      'message': 'Invalid addresses, supported '
                                                 + type_field + ' : ' + ', '.join(
                                          address_types)}}
            elif key == 'phone_numbers':
                type_field = 'phone_number_type'
                phone_number_types = []
                for fk in fields[key]:
                    params_type, text = util.get_params_value(fk[type_field], None)
                    phone_number_types.append(text)

                if not isinstance(input_dict[key], list):
                    return {
                        'error': {'id': 'Bad Request', 'status_code': 400,
                                  'message': 'Invalid phone_numbers, phone_numbers should be an array'}}

                for phone_number in input_dict[key]:

                    try:
                        m = next(i for i in fields[key] if
                                 i[type_field].lower() == '${constant.' + phone_number.get(type_field,
                                                                                           '').lower() + '}')
                        for p_n in phone_number:
                            if p_n == type_field:
                                continue
                            if p_n in m:
                                properties_dict[m[p_n]] = phone_number[p_n]
                            else:
                                return {
                                    'error': {'id': 'Bad Request', 'status_code': 400,
                                              'message': 'Invalid phone_numbers property ' + p_n}}
                    except StopIteration:
                        return {
                            'error': {'id': 'Bad Request', 'status_code': 400,
                                      'message': 'Invalid phone_numbers, supported ' + type_field + ' : ' + ', '.join(
                                          phone_number_types)}}

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


def create_deal(auth, input_dict, fields):
    url = "https://api.hubapi.com/crm/v3/objects/deals"
    return upsert_deal(auth, url, input_dict, fields, None)


def update_deal(auth, obj_id, input_dict, fields):
    url = "https://api.hubapi.com/crm/v3/objects/deals/" + obj_id
    return upsert_deal(auth, url, input_dict, fields, obj_id)


def create_contact(auth, input_dict, fields):
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    return upsert_contact(auth, url, input_dict, fields, None)


def update_contact(auth, obj_id, input_dict, fields):
    url = "https://api.hubapi.com/crm/v3/objects/contacts/" + obj_id
    return upsert_contact(auth, url, input_dict, fields, obj_id)


def upsert_contact(auth, url, input_dict, fields, obj_id):
    properties_dict = {}
    custom_fields = {}
    for key in input_dict:
        if key in fields:
            if key == 'email_addresses':
                type_field = 'email_address_type'
                email_types = []
                for fk in fields[key]:
                    params_type, text = util.get_params_value(fk[type_field], None)
                    email_types.append(text)
                if not isinstance(input_dict[key], list):
                    return {
                        'error': {'id': 'Bad Request', 'status_code': 400,
                                  'message': 'Invalid email_addresses, email addresses should be an array'}}
                for email in input_dict[key]:

                    try:
                        m = next(i for i in fields[key] if
                                 i[type_field].lower() == '${constant.' + email.get(type_field, '').lower() + '}')
                        for e in email:
                            if e == type_field:
                                continue
                            if e in m:
                                properties_dict[m[e]] = email[e]
                            else:
                                return {'error': {'id': 'Bad Request', 'status_code': 400,
                                                  'message': 'Invalid email_addresses property ' + e}}
                    except StopIteration:
                        return {'error': {'id': 'Bad Request', 'status_code': 400,
                                          'message': 'Invalid email_addresses, supported ' + type_field + ' : ' + ', '.join(
                                              email_types)}}
            elif key == 'addresses':
                type_field = 'address_type'
                address_types = []
                for fk in fields[key]:
                    params_type, text = util.get_params_value(fk[type_field], None)
                    address_types.append(text)

                if not isinstance(input_dict[key], list):
                    return {
                        'error': {'id': 'Bad Request', 'status_code': 400, 'message': 'Invalid addresses, addresses '
                                                                                      'should be an array'}}
                for address in input_dict[key]:
                    street_1 = address.get('street_1', '')
                    street_2 = address.get('street_2', '')
                    full_street = street_1
                    if street_2:
                        if full_street:
                            full_street += ' '
                        full_street += street_2
                    if full_street:
                        address['street_1'] = full_street
                    try:
                        m = next(i for i in fields[key] if
                                 i[type_field].lower() == '${constant.' + address.get(type_field, '').lower() + '}')
                        for a in address:
                            if a == type_field:
                                continue
                            if a in m:
                                if not m[a]:
                                    continue
                                properties_dict[m[a]] = address[a]
                            else:
                                return {'error': {'id': 'Bad Request', 'status_code': 400,
                                                  'message': 'Invalid addresses property ' + a}}
                    except StopIteration:
                        return {
                            'error': {'id': 'Bad Request', 'status_code': 400,
                                      'message': 'Invalid addresses, supported ' + type_field + ' : ' + ', '.join(
                                          address_types)}}
            elif key == 'phone_numbers':
                type_field = 'phone_number_type'
                phone_number_types = []
                for fk in fields[key]:
                    params_type, text = util.get_params_value(fk[type_field], None)
                    phone_number_types.append(text)

                if not isinstance(input_dict[key], list):
                    return {
                        'error': {'id': 'Bad Request', 'status_code': 400,
                                  'message': 'Invalid phone_numbers, phone_numbers should be an array'}}
                for phone_number in input_dict[key]:
                    try:
                        m = next(i for i in fields[key] if
                                 i[type_field].lower() == '${constant.' + phone_number.get(type_field,
                                                                                           '').lower() + '}')
                        for p_n in phone_number:
                            if p_n == type_field:
                                continue
                            if p_n in m:
                                properties_dict[m[p_n]] = phone_number[p_n]
                            else:
                                return {'error': {'id': 'Bad Request', 'status_code': 400,
                                                  'message': 'Invalid phone_numbers property ' + p_n}}
                    except StopIteration:
                        return {
                            'error': {'id': 'Bad Request', 'status_code': 400,
                                      'message': 'Invalid phone_numbers, supported ' + type_field + ' : ' + ', '.join(
                                          phone_number_types)}}

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


def upsert_deal(auth, url, input_dict, fields, obj_id):
    properties_dict = {}
    custom_fields = {}
    account_id = None
    for key in input_dict:
        if key in fields:
            if key == 'status':
                continue
            elif key == 'stage_id':
                stages = get_pipelines(auth)
                try:
                    m = next(i for i in stages['results'] if i['id'] == input_dict[key])
                    properties_dict['pipeline'] = m['pipeline_id']
                    properties_dict['dealstage'] = m['stage_id']
                except StopIteration:
                    return {'error': {'id': 'Bad Request', 'status_code': 400,
                                      'message': 'Invalid stage_id'}}
            elif key == 'account_id':
                account_id = input_dict[key]
            elif key == 'close_date':
                close_date = convert_iso_date_to_timestamp(input_dict[key])
                if not close_date:
                    return {'error': {'id': 'Bad Request', 'status_code': 400,
                                      'message': 'Invalid close_date, please use ISO-8601 format YYYY-MM-DDT00:00:00Z'}}
                properties_dict[fields[key]] = close_date
            else:
                properties_dict[fields[key]] = input_dict[key]
        else:
            properties_dict[key] = input_dict[key]
            custom_fields[key] = input_dict[key]
    result = {}
    is_new = False
    if not obj_id:
        is_new = True
        result = insert_object(auth, url, properties_dict)
    elif len(properties_dict) > 0:
        result = patch_object(auth, url, properties_dict, obj_id)
    elif not account_id:
        return {'error': {'id': 'Bad Request', 'status_code': 400,
                          'message': 'No properties found to update, please provide at least one.'}}
    if 'error' in result:
        return {'error': result['error']}

    if 'id' in result:
        obj_id = result['id']
    if account_id and obj_id:
        r = create_associations(auth, obj_id, account_id, 5)
        if 'error' in r:
            return {'error': r['error']}
    if len(result) > 0:
        return result
    elif is_new:
        return {'id': obj_id, 'created_at': util.get_now_iso_format()}
    else:
        return {'id': obj_id, 'updated_at': util.get_now_iso_format()}


def convert_iso_date_to_timestamp(ios_date):
    try:
        utc_dt = datetime.strptime(ios_date, '%Y-%m-%dT%H:%M:%SZ')
        timestamp = int((utc_dt - datetime(1970, 1, 1)).total_seconds() * 1000)
    except ValueError:
        return None
    return timestamp


def query_object_by_id(auth, url, common_model, custom_model):
    result = ru.get_request_with_bearer(url, auth)

    result_dict = {}
    if result.success:
        result_dict['data'] = get_result_from_model(result.json_body['properties'], common_model, custom_model)
    else:
        result_dict['error'] = {}
        result_dict['error']['id'] = result.error_description
        result_dict['error']['status_code'] = result.status_code
        if result.json_body:
            result_dict['error']['message'] = result.json_body.get('message', result.json_body)
    return result_dict


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
    return result


def query_objects_by_ids_batch(auth, url, obj_ids: [], properties, fields, custom_fields):
    processing_ids = obj_ids
    results = []
    data = {}
    while len(processing_ids) > 0:
        if len(processing_ids) > 100:
            subset_ids = processing_ids[: 100]
            processing_ids = processing_ids[100:]
        else:
            subset_ids = processing_ids
            processing_ids = []
        d = query_objects_by_ids(auth, url, subset_ids, properties, fields, custom_fields)

        if 'error' in d:
            data['error'] = d['error']
        else:
            results += d['results']
    data['results'] = results
    return data


def query_objects_by_filter(auth, url, properties, common_model, custom_model, filters, limit, after):
    filter_requests = []
    request_data = {}
    for f in filters:
        operator = f.get('filter_operator', '')
        field = f.get('filter_field', '')
        if not operator or not field:
            continue
        filter_object = {'propertyName': field, 'operator': operator}
        if operator == 'IN' or operator == 'NOT_IN':
            filter_object['values'] = f.get('filter_values', [])
        if operator == 'EQ' or operator == 'BETWEEN' or operator == 'LT' or operator == 'LTE' or operator == 'GT' or operator == 'GTE' or operator == 'NEQ' or operator == 'CONTAINS_TOKEN' or operator == 'NOT_CONTAINS_TOKEN':
            filter_object['value'] = f.get('filter_value', '')
        if operator == 'BETWEEN':
            filter_object['highValue'] = f.get('filter_high_value', '')
        filter_requests.append(filter_object)
    request_data['filters'] = filter_requests
    request_data['properties'] = properties
    request_data['limit'] = limit
    if after:
        request_data['after'] = after
    result = ru.post_request_with_bearer(url, auth, request_data)
    data = {'results': []}
    if result.success:
        for r in result.json_body['results']:
            result_dict = {'id': r['id'], 'data': get_result_from_model(r['properties'], common_model, custom_model)}
            data['results'].append(result_dict)
        if 'paging' in result.json_body and 'next' in result.json_body['paging'] and 'after' in \
                result.json_body['paging']['next']:
            next_cursor = result.json_body['paging']['next'].get('after', '')
            if next_cursor:
                data['next_cursor'] = next_cursor
    else:
        data['error'] = {}
        data['error']['id'] = result.error_description
        data['error']['status_code'] = result.status_code
        if result.json_body:
            data['error']['message'] = result.json_body.get('message', result.json_body)
    return data


def query_objects_by_ids(auth, url, obj_ids: [], properties, common_model, custom_model):
    request_data = {'inputs': []}
    for obj_id in obj_ids:
        request_data['inputs'].append({'id': obj_id})
    request_data['properties'] = properties
    result = ru.post_request_with_bearer(url, auth, request_data)
    data = {'results': []}
    if result.success:
        for r in result.json_body['results']:
            result_dict = {'id': r['id'], 'data': get_result_from_model(r['properties'], common_model, custom_model)}
            data['results'].append(result_dict)
    else:
        data['error'] = {}
        data['error']['id'] = result.error_description
        data['error']['status_code'] = result.status_code
        if result.json_body:
            data['error']['message'] = result.json_body.get('message', result.json_body)
    return data


def get_properties(auth, url):
    result = ru.get_request_with_bearer(url, auth)
    if result.success:
        return result.json_body
    return []


def get_datetime_fields(properties, common_models, custom_model):
    datetime_properties = [x['name'] for x in properties if x['type'] == 'datetime']
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
            property_obj = next(i for i in properties if i['name'] == original_key_name)
            field_obj = {'id': key, 'display_name': property_obj['label'], 'origin_key_name': original_key_name,
                         'description': property_obj['description'], 'is_custom': is_custom}
            options = property_obj['options']
            options.sort(key=lambda x: x['displayOrder'], reverse=False)
            field_type = property_obj['fieldType']
            field_obj['field_choices'] = []
            field_obj['field_format'] = ''
            field_obj['is_required'] = False
            if property_obj['type'] == 'number':
                field_obj['field_type'] = 'number'
                if property_obj['numberDisplayHint'] == 'percentage':
                    field_obj['field_format'] = 'percentage'
                elif property_obj['numberDisplayHint'] == 'currency':
                    field_obj['field_format'] = 'currency'
            elif len(options) > 0:
                if field_type == 'checkbox':
                    field_obj['field_type'] = 'multiselect'
                elif field_type == 'booleancheckbox':
                    field_obj['field_type'] = 'select'
                    field_obj['field_format'] = 'checkbox'
                else:
                    field_obj['field_type'] = 'select'
                for opt in options:
                    field_obj['field_choices'].append({'label': opt['label'], 'value': opt['value']})
            elif property_obj['type'] == 'datetime':
                field_obj['field_type'] = 'datetime'
            elif property_obj['type'] == 'phone_number':
                field_obj['field_type'] = 'text'
                field_obj['field_format'] = 'phone'
            else:
                field_obj['field_type'] = field_type

            field_properties.append(field_obj)
        except StopIteration:
            continue

    return field_properties


def insert_object(auth, url, properties_dict):
    request_data = {"properties": properties_dict}
    result = ru.post_request_with_bearer(url, auth, request_data)
    data = {}
    if result.success:
        data['id'] = result.json_body['id']
        data['created_at'] = get_normalized_data(result.json_body, 'createdAt')
    else:
        data['error'] = {}
        data['error']['id'] = result.error_description
        data['error']['status_code'] = result.status_code
        if result.json_body:
            data['error']['message'] = result.json_body.get('message', result.json_body)
    return data


def patch_object(auth, url, properties_dict, obj_id):
    request_data = {"properties": properties_dict}
    result = ru.patch_request_with_bearer(url, auth, request_data)
    data = {}
    if result.success:
        data['id'] = result.json_body['id']
        data['updated_at'] = get_normalized_data(result.json_body, 'updatedAt')
    else:
        data['error'] = {}
        data['error']['id'] = result.error_description
        data['error']['status_code'] = result.status_code
        if result.json_body:
            data['error']['message'] = result.json_body.get('message', result.json_body)
    return data


def get_owner_by_id(auth, obj_id, fields, include_field_properties):
    url = 'https://api.hubapi.com/owners/v2/owners'
    result = ru.get_request_with_bearer(url, auth)
    data = {'id': obj_id}
    if result.success:
        try:
            m = next(i for i in result.json_body if
                     str(i['ownerId']) == str(obj_id))
            r = get_result_from_model(m, fields, None)
            owner = {'id': obj_id, 'data': r}
            if include_field_properties:
                owner['field_properties'] = get_user_properties(fields, r)
            return owner
        except StopIteration:
            data['error'] = {}
            data['error']['id'] = 'Not found'
            data['error']['status_code'] = 404
    else:
        data['error'] = {}
        data['error']['id'] = result.error_description
        data['error']['status_code'] = result.status_code
        if result.json_body:
            data['error']['message'] = result.json_body.get('message', result.json_body)
    return data


def get_owners(auth, obj_ids, fields, include_field_properties,
               created_before, created_after, modified_before, modified_after):
    url = 'https://api.hubapi.com/owners/v2/owners'
    result = ru.get_request_with_bearer(url, auth)
    data = {'results': []}

    if result.success:
        owners = result.json_body
        if obj_ids and len(obj_ids) > 0:
            owners = [x for x in result.json_body if str(x['ownerId']) in obj_ids]
        elif created_before:
            owners = [x for x in result.json_body if x['createdAt'] < int(created_before)]
        elif created_after:
            owners = [x for x in result.json_body if x['createdAt'] >= int(created_after)]
        elif modified_before:
            owners = [x for x in result.json_body if x['updatedAt'] < int(modified_before)]
        elif modified_after:
            owners = [x for x in result.json_body if x['updatedAt'] >= int(modified_after)]

        for r in owners:
            owner = get_result_from_model(r, fields, None)
            result_dict = {'id': str(r['ownerId']), 'data': owner}
            if include_field_properties:
                result_dict['field_properties'] = get_user_properties(fields, owner)
            data['results'].append(result_dict)
    else:
        data['error'] = {}
        data['error']['id'] = result.error_description
        data['error']['status_code'] = result.status_code
        if result.json_body:
            data['error']['message'] = result.json_body.get('message', result.json_body)
    return data


def get_user_properties(fields, values):
    properties = [{'name': 'email', 'description': 'owner email address', 'label': 'email', 'fieldType': 'text'},
                  {'name': 'isActive', 'description': 'whether owner account is active', 'label': 'Is Active',
                   'fieldType': 'boolean'}]
    field_properties = []
    for key in values:
        original_key_name = key
        is_custom = False
        if key in fields:
            if not fields[key]:
                continue
            if '$' in fields[key]:
                continue
            original_key_name = fields[key]

        property_obj = next(i for i in properties if i['name'] == original_key_name)
        field_obj = {'id': key, 'display_name': property_obj['label'], 'origin_key_name': original_key_name,
                     'description': property_obj['description'], 'is_custom': is_custom, 'field_choices': [],
                     'field_format': None,
                     'field_type': property_obj['fieldType'], 'value': values.get(key, None)}
        field_properties.append(field_obj)
    return field_properties


def get_deal_by_id(auth, obj_id, fields, custom_fields, include_field_properties):
    url = "https://api.hubapi.com/crm/v3/objects/deals/" + str(obj_id)
    url_params = ''
    properties = get_properties_from_model(fields, custom_fields)
    for p in properties:
        url_params += "&properties=" + p
    url += '?' + url_params
    deal = query_object_by_id(auth, url, fields, custom_fields)
    result = {'id': obj_id}

    url_properties = "https://api.hubapi.com/properties/v1/deals/properties"
    properties_details = get_properties(auth, url_properties)

    if 'data' in deal:
        if not include_field_properties:
            datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)
            for df in datetime_fields:
                deal['data'][df] = get_normalized_datetime(deal['data'].get(df, None))
    elif 'error' in deal:
        result['error'] = deal['error']
        return result

    association_url = "https://api.hubapi.com/crm/v3/associations/deal/company/batch/read"
    associations = query_associations_by_ids_batch(auth, association_url, [obj_id])

    try:
        m = next(i for i in associations['results'] if
                 i['id'] == obj_id)
        if len(m['associated_ids']) > 0:
            deal['data']['account_id'] = m['associated_ids'][0]
    except StopIteration:
        deal['data']['account_id'] = None

    field_properties = None
    if include_field_properties and 'data' in deal:
        field_properties = get_fields_properties(properties_details, fields, custom_fields)
        for p in field_properties:
            if p['field_type'] == 'datetime':
                deal['data'][p['id']] = get_normalized_datetime(deal['data'].get(p['id'], None))
            p['value'] = deal['data'].get(p['id'], None)

    if 'data' in deal:
        result['data'] = deal['data']
    if field_properties:
        result['field_properties'] = field_properties
    return result


def get_deals_by_filter(auth, fields, custom_fields, include_field_properties, owner_id, created_before,
                        created_after, modified_before, modified_after, limit, cursor):
    url = "https://api.hubapi.com/crm/v3/objects/deals/search"
    properties = get_properties_from_model(fields, custom_fields)

    filters = []
    if owner_id:
        f = {'filter_field': 'hubspot_owner_id', 'filter_operator': 'EQ', 'filter_value': owner_id}
        filters.append(f)
    elif created_before:
        f = {'filter_field': 'createdate', 'filter_operator': 'LT', 'filter_value': int(created_before)}
        filters.append(f)
    elif created_after:
        f = {'filter_field': 'createdate', 'filter_operator': 'GTE', 'filter_value': int(created_after)}
        filters.append(f)
    elif modified_before:
        f = {'filter_field': 'hs_lastmodifieddate', 'filter_operator': 'LT',
             'filter_value': int(modified_before)}
        filters.append(f)
    elif modified_after:
        f = {'filter_field': 'hs_lastmodifieddate', 'filter_operator': 'GTE',
             'filter_value': int(modified_after)}
        filters.append(f)
    if not limit:
        limit = '100'
    data = query_objects_by_filter(auth, url, properties, fields, custom_fields, filters, limit, cursor)
    deals = data['results']

    association_url = "https://api.hubapi.com/crm/v3/associations/deal/company/batch/read"
    associations = query_associations_by_ids_batch(auth, association_url, list([d['id'] for d in deals]))

    url_properties = "https://api.hubapi.com/properties/v1/deals/properties"
    properties_details = get_properties(auth, url_properties)

    datetime_fields = []
    if not include_field_properties:
        datetime_fields = get_datetime_fields(properties_details, fields, custom_fields)

    for deal in deals:
        for df in datetime_fields:
            deal['data'][df] = get_normalized_datetime(deal['data'].get(df, None))
        try:
            m = next(i for i in associations['results'] if
                     str(i['id']) == str(deal['id']))
            if len(m['associated_ids']) > 0:
                deal['data']['account_id'] = m['associated_ids'][0]
        except StopIteration:
            continue

    if include_field_properties:
        field_properties = get_fields_properties(properties_details, fields, custom_fields)
        for deal in deals:
            deal['field_properties'] = copy.deepcopy(field_properties)
            for p in deal['field_properties']:
                if p['field_type'] == 'datetime':
                    deal['data'][p['id']] = get_normalized_datetime(deal['data'].get(p['id'], None))
                p['value'] = deal['data'].get(p['id'], None)

    result = {'results': deals}
    if 'error' in data:
        result['error'] = data['error']
    if 'next_cursor' in data:
        result['next_cursor'] = data['next_cursor']
    return result


def get_stage_by_id(auth, obj_id, fields, include_field_properties):
    result = get_pipelines(auth)
    data = {'id': obj_id}
    if 'error' in result:
        data['error'] = result['error']
        return data

    stages = result['results']
    try:
        m = next(i for i in stages if
                 i['id'] == obj_id)
        stage = get_result_from_model(m, fields, None)
        data['data'] = stage
        if include_field_properties:
            data['field_properties'] = []
    except StopIteration:
        data['error'] = {}
        data['error']['id'] = 'Not found'
        data['error']['status_code'] = 404
    return data


def get_stages(auth, obj_ids, fields, include_field_properties,
               created_before, created_after, modified_before, modified_after):
    result = get_pipelines(auth)
    stages = result['results']
    data = {'results': []}
    if obj_ids and len(obj_ids) > 0:
        stages = [x for x in stages if str(x['id']) in obj_ids]
    if created_before:
        stages = [x for x in stages if x['createdAt'] < int(created_before)]
    elif created_after:
        stages = [x for x in stages if x['createdAt'] >= int(created_after)]
    elif modified_before:
        stages = [x for x in stages if x['updatedAt'] < int(modified_before)]
    elif modified_after:
        stages = [x for x in stages if x['updatedAt'] >= int(modified_after)]
    for s in stages:
        stage = get_result_from_model(s, fields, None)
        result_dict = {'id': str(s['id']), 'data': stage}
        if include_field_properties:
            result_dict['field_properties'] = []
        data['results'].append(result_dict)
    if 'error' in result:
        data['error'] = result['error']
    return data


def get_pipelines(auth):
    url = 'https://api.hubapi.com/crm-pipelines/v1/pipelines/deals'
    result = ru.get_request_with_bearer(url, auth)
    results = []
    data = {}
    if result.success:
        pipeline = result.json_body['results']
        pipeline.sort(key=lambda x: x['displayOrder'], reverse=False)
        for p in pipeline:
            pipeline_id = p['pipelineId']
            pipeline_label = p['label']
            stages = p['stages']
            stages.sort(key=lambda x: x['displayOrder'], reverse=False)
            for s in stages:
                stage_id = s['stageId']
                stage_label = s['label']
                combined_id = str(pipeline_id) + str(stage_id)
                results.append(
                    {'stage_id': stage_id, 'pipeline_id': pipeline_id, 'pipeline': pipeline_label, 'stage': stage_label,
                     'createdAt': s['createdAt'], 'updatedAt': s['updatedAt'], 'id': combined_id})
    else:
        data['error'] = {}
        data['error']['id'] = result.error_description
        data['error']['status_code'] = result.status_code
        if result.json_body:
            data['error']['message'] = result.json_body.get('message', result.json_body)
    data['results'] = results
    return data


def query_associations_by_ids_batch(auth, url, obj_ids: []):
    processing_ids = obj_ids
    results = []
    data = {}
    while len(processing_ids) > 0:
        if len(processing_ids) > 100:
            subset_ids = processing_ids[: 100]
            processing_ids = processing_ids[100:]
        else:
            subset_ids = processing_ids
            processing_ids = []
        d = query_associations(auth, subset_ids, url)

        if 'error' in d:
            data['error'] = d['error']
        else:
            results += d['results']
    data['results'] = results
    return data


def query_associations(auth, obj_ids, url):
    request_data = {'inputs': []}
    for obj_id in obj_ids:
        request_data['inputs'].append({'id': obj_id})
    result = ru.post_request_with_bearer(url, auth, request_data)
    associations = []
    if result.success:
        for r in result.json_body['results']:
            from_id = str(r['from']['id'])
            association = {"id": from_id, "associated_ids": []}
            for t in r['to']:
                association['associated_ids'].append(str(t['id']))
            associations.append(association)
    return {'results': associations}


def create_associations(auth, from_object_id, to_object_id, definitionId):
    url = 'https://api.hubapi.com/crm-associations/v1/associations'
    request_object = {'fromObjectId': from_object_id, 'toObjectId': to_object_id, "category": "HUBSPOT_DEFINED",
                      "definitionId": definitionId}
    result = ru.put_request_with_bearer(url, auth, request_object)
    data = {}
    if result.success:
        return data
    else:
        data['error'] = {}
        data['error']['id'] = result.error_description
        data['error']['status_code'] = result.status_code
        if result.json_body:
            data['error']['message'] = result.json_body.get('message', result.json_body)
    return data


def get_normalized_data(data, key):
    if not data.get(key, None):
        return None
    match key:
        case 'createdAt' | 'updatedAt':
            data[key] = get_normalized_datetime(data[key])
        case _:
            return data[key]
    return data[key]


def get_normalized_datetime(hubspot_datetime):
    if not hubspot_datetime:
        return None
    date_parts = hubspot_datetime.split('.')
    if len(date_parts) == 2:
        return date_parts[0] + 'Z'
    return hubspot_datetime
