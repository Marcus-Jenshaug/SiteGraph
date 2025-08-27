import yaml
import os

DEFAULT_CONFIG = {
    'start_url': None,
    'include_subdomains': False,
    'max_pages': 20000,
    'max_depth': 12,
    'concurrency': 8,
    'render_js': True,
    'respect_robots': True,
    'crawl_delay_ms': 300,
    'allowed_paths': ["/"],
    'blocked_paths': [],
    'auth': None,
    'language': 'nb-NO',
    'mask_query_params': [],
    'db': 'crawl.db',
    'output_dir': 'report'
}

def load_config(config_path: str) -> dict:
    """
    Loads configuration from a YAML file, merges it with defaults,
    and performs basic validation.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path, 'r') as f:
        user_config = yaml.safe_load(f)

    config = {**DEFAULT_CONFIG, **user_config}

    if not config.get('start_url'):
        raise ValueError("'start_url' is a required configuration parameter.")

    return config
