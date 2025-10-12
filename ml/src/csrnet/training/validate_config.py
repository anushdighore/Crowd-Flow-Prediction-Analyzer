"""Validate YAML config file syntax"""
import yaml
from pathlib import Path

config_path = Path(__file__).parents[4] / "ml" / "csrnet_config.yaml"

try:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print("✓ YAML syntax is VALID!")
    print(f"\nKey sections found:")
    for key in config.keys():
        print(f"  - {key}")
    
    print(f"\nCritical settings:")
    print(f"  batch_size: {config['training']['hyperparameters']['batch_size']}")
    print(f"  num_workers: {config['training']['dataloader']['num_workers']}")
    print(f"  device.cuda: {config['device']['cuda']}")
    
except yaml.YAMLError as e:
    print(f"✗ YAML SYNTAX ERROR:")
    print(f"  {e}")
except Exception as e:
    print(f"✗ ERROR:")
    print(f"  {e}")
