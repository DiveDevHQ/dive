import copy
from collections import ChainMap
import re
from datetime import datetime


def get_params_value(text, data):
    variables = re.findall(r'\{(.*?)\}', text)
    params_type = None
    for v in variables:
        parts = [s.strip() for s in v.split('.')]
        if len(parts) > 1:
            params_type = parts[0]
            if params_type == 'constant':
                text = text.replace('${constant.' + parts[1] + '}', parts[1])
            elif params_type == 'reference' and data:
                if len(parts) == 2 and data.get(parts[1], None):
                    text = text.replace('${reference.' + parts[1] + '}', data[parts[1]])
                elif len(parts) == 3 and data.get(parts[1], None) and data[parts[1]].get(parts[2], None):
                    text = text.replace('${reference.' + parts[1] + '.' + parts[2] + '}',
                                        data[parts[1]][parts[2]])
                else:
                    text = None

    return params_type, text


def get_now_iso_format():
    now = datetime.now()
    iso_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return iso_time


def merge_two_dict(first_dict, second_dict):
    return dict(ChainMap({}, second_dict, first_dict))


def merge_model(common_model, custom_model):
    if not custom_model or len(custom_model) == 0:
        return common_model
    result_dict = copy.deepcopy(common_model)
    for m in custom_model:
        result_dict[m] = m
    return result_dict


def get_params_keys(text):
    keys = []
    variables = re.findall(r'\{(.*?)\}', text)
    for v in variables:
        parts = [s.strip() for s in v.split('.')]
        if len(parts) > 1:
            if parts[0] == 'reference':
                keys.append(parts[1])
    return keys
