from django.apps import AppConfig
from pathlib import Path

import yaml

class IntegrationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'integrations'
    base_path = Path(__file__).parent
    config_path = (base_path / "config.yaml").resolve()
    with open(config_path) as f:
        integration_config = yaml.safe_load(f)



