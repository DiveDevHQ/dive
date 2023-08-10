from pathlib import Path
import json
import integrations.connectors.connectors_utils as util
import environ

env = environ.Env()
environ.Env.read_env()


def get_objects(auth, app, obj_type, schema):
    field_dict = json.loads(schema)
    data = util.load_file_from_url(field_dict["name"], field_dict["name"], field_dict['file_url'],
                                   field_dict['mime_type'], None, True)
    return {'results': data}


def load_objects(auth, app, obj_type, modified_after, cursor, schema):
    return get_objects(auth, app, obj_type, schema)
