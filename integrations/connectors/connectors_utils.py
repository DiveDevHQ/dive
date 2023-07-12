import copy
from collections import ChainMap
import re
from datetime import datetime
from io import BytesIO
import pypdf
import requests


def get_params_value(text, data):
    variables = re.findall(r'\{(.*?)\}', text)
    params_type = None
    has_formula = False
    for v in variables:
        parts = [s.strip() for s in v.split('.')]
        if len(parts) > 1:
            params_type = parts[0]
            if params_type == 'constant':
                text = text.replace('${constant.' + parts[1] + '}', parts[1])
            elif params_type == 'reference' and data:
                if len(parts) == 2 and parts[1] in data:
                    text = text.replace('${reference.' + parts[1] + '}', str(data[parts[1]]))
                elif len(parts) == 3 and data.get(parts[1], None) and data[parts[1]].get(parts[2], None):
                    text = text.replace('${reference.' + parts[1] + '.' + parts[2] + '}',
                                        data[parts[1]][parts[2]])
                else:
                    text = None
            elif params_type == 'formula' and data:
                has_formula = True
                if len(parts) == 2 and parts[1] in data:
                    text = text.replace('${formula.' + parts[1] + '}', str(data[parts[1]]))
    if has_formula:
        text = get_value_from_formula(text)
    return params_type, text


def get_value_from_formula(text):
    text = text.strip()
    if 'IF' in text:
        formula_start = text[text.find("IF") + 2:]
        formula_text = formula_start[formula_start.find("(") + 1:-1]
        eval_text = formula_text[:formula_text.find(',')]
        result_text = formula_text[formula_text.find(',') + 1:]
        if 'IF' in result_text:
            ifs = re.findall('IF\(([^)]+)\)', result_text)
            if len(ifs) == 2:
                if eval(eval_text.strip()):
                    return get_value_from_formula('IF(' + ifs[0] + ')')
                else:
                    return get_value_from_formula('IF(' + ifs[1] + ')')
            elif len(ifs) == 1:
                coma_index = result_text.find(",")
                if_index = result_text.find("IF")

                if coma_index < if_index:
                    if eval(eval_text.strip()):
                        return result_text.split(',')[0].strip()
                    else:
                        return get_value_from_formula('IF(' + ifs[0] + ')')
                else:
                    if eval(eval_text.strip()):
                        return get_value_from_formula('IF(' + ifs[0] + ')')
                    else:
                        return result_text.split(',')[-1].strip()
        else:
            result_parts = result_text.split(',')
            if eval(eval_text.strip()):
                return result_parts[0].strip()
            else:
                return result_parts[1].strip()


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
            if parts[0] == 'reference' or parts[0] == 'formula':
                keys.append(parts[1])
    return keys


def pdf_load_from_url(doc_id, file_name, file_url, extra_info):
    r = requests.get(file_url)
    with BytesIO(r.content) as data:
        docs = []
        read_pdf = pypdf.PdfReader(data)
        part = 0
        for page in range(len(read_pdf.pages)):
            page_text = read_pdf.pages[page].extract_text()
            page_label = read_pdf.page_labels[page]
            metadata = {"page_label": page_label, "file_name": file_name}
            if extra_info is not None:
                metadata.update(extra_info)
            docs.append({'id': f"{str(doc_id)}_part_{part}", 'data': page_text, 'metadata': metadata})
            part += 1
        return docs

