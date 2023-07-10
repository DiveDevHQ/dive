import json
from pathlib import Path
import integrations.connectors.connectors_utils as util
import requests, PyPDF2
from io import BytesIO


def get_objects(auth, app, obj_type, schema):
    if schema:
        field_dict = json.loads(schema)
    else:
        base_path = Path(__file__).parent
        try:
            with open(str(base_path) + '/schemas/' + obj_type + '.json') as f:
                field_dict = json.load(f)

        except FileNotFoundError:
            return

    r = requests.get(field_dict['file_url'])
    my_raw_data = r.content
    contents = ""
    with BytesIO(my_raw_data) as data:
        read_pdf = PyPDF2.PdfReader(data)
        for page in range(len(read_pdf.pages)):
            contents += read_pdf.pages[page].extract_text()+'\n'

    data = {'results': [{'id': field_dict["name"], 'data': {'content': contents}}]}
    return data


def load_objects(auth, app, obj_type, modified_after, cursor, schema):
    return get_objects(auth, app, obj_type, schema)
