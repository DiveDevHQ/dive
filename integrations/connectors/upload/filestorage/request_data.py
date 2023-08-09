from pathlib import Path
import json
import integrations.connectors.connectors_utils as util
import environ

env = environ.Env()
environ.Env.read_env()
import os


def get_objects(auth, app, obj_type, schema):
    field_dict = json.loads(schema)
    supabase_folder = env.str('SUPABASE_FOLDER_PATH', default='') or os.environ.get('SUPABASE_FOLDER_PATH', '')
    supabase_auth = env.str('SUPABASE_AUTH_TOKEN', default='') or os.environ.get('SUPABASE_AUTH_TOKEN', '')
    data = util.load_file_from_url(field_dict["name"], field_dict["name"], supabase_folder + field_dict['file_url'],
                                   field_dict['mime_type'], None, supabase_auth)
    return {'results': data}


def load_objects(auth, app, obj_type, modified_after, cursor, schema):
    return get_objects(auth, app, obj_type, schema)
