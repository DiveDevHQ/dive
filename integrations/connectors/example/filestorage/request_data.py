import json
from pathlib import Path
import integrations.connectors.connectors_utils as util


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

    data = util.load_file_from_url(field_dict["name"], field_dict["name"], field_dict['file_url'],
                                   field_dict['mime_type'], None, None)
    return {'results': data}


def load_objects(auth, app, obj_type, modified_after, cursor, schema):
    return get_objects(auth, app, obj_type, schema)
