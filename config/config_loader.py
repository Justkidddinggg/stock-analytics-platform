import yaml
import os
import logging

logger = logging.getLogger(__name__)

def load_config(config_path: str = None) -> dict:
    """
    โหลด config จาก yaml file
    """
    if config_path is None:
        # หา config.yaml อัตโนมัติ
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'config', 'config.yaml')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    logger.info(f"✅ Config loaded from {config_path}")
    return config

if __name__ == "__main__":
    config = load_config()
    print(config)