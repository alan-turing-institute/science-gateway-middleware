import os


# Import local config variables for test
def ensure_instance_config_exists():
    config_path = "instance/config.py"
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            f.write("")
