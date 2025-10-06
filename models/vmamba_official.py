import logging
import importlib
import sys
from pathlib import Path
from typing import Optional

import torch

logger = logging.getLogger(__name__)

def load_tmtb_model(checkpoint_path: str, device: Optional[str] = None):
    """Load official VMamba-TMTB model"""
    try:
        # Add official model path
        current_dir = Path(__file__).resolve().parent
        project_root = current_dir.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        candidate_modules = [
            'architectures.taste_more_taste_better.model.model',
            'models.official.model',
        ]

        mamba = None
        selected_module = None
        for module_name in candidate_modules:
            try:
                module = importlib.import_module(module_name)
                mamba = getattr(module, 'mamba')
                selected_module = module_name
                break
            except (ImportError, AttributeError):
                continue

        if mamba is None:
            raise ImportError("Unable to locate VMamba architecture module")

        logger.info(f"Using VMamba architecture from: {selected_module}")
        
        logger.info(f"Loading official VMamba-TMTB from: {checkpoint_path}")
        
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Create model exactly like the official test.py
        model = mamba(num_classes=25, vmamba_path=None, strict_backbone=False)

        checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)

        if isinstance(checkpoint, dict):
            if 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            elif 'model' in checkpoint:
                state_dict = checkpoint['model']
            else:
                state_dict = {
                    key.replace('module.', ''): value
                    for key, value in checkpoint.items()
                    if isinstance(value, torch.Tensor)
                }
        else:
            state_dict = checkpoint

        # Fix checkpoint key naming: decoder -> count in reg_head
        # The checkpoint was trained with CountingHead that used self.decoder
        # but current architecture uses self.count
        from collections import OrderedDict
        corrected_state_dict = OrderedDict()
        keys_renamed = 0
        for key, value in state_dict.items():
            if 'reg_head.count.decoder' in key:
                new_key = key.replace('reg_head.count.decoder', 'reg_head.count.count')
                corrected_state_dict[new_key] = value
                keys_renamed += 1
            else:
                corrected_state_dict[key] = value
        
        if keys_renamed > 0:
            logger.info(f"🔧 Fixed {keys_renamed} checkpoint keys (decoder->count)")
            state_dict = corrected_state_dict

        missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
        
        # Count parameters
        total_params = sum(p.numel() for p in model.parameters())
        logger.info(f"✅ Official model loaded: {total_params:,} parameters")
        if missing_keys:
            logger.info(f"⚠️ Missing {len(missing_keys)} keys (this is normal)")
        if unexpected_keys:
            logger.info(f"⚠️ Unexpected {len(unexpected_keys)} keys (this is normal)")

        model.to(device)
        model.eval()

        logger.info("🚀 Official VMamba-TMTB ready for inference!")

        return model

    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Trying alternative import strategy...")
        
        # FALLBACK: Try to fix the relative imports in the official files
        try:
            # Go back to your working custom implementation as backup
            logger.info("🔄 Falling back to custom VMamba implementation...")
            sys.path.append('./models')
            from vmamba_tmtb import load_tmtb_model as custom_load
            return custom_load(checkpoint_path, device)
            
        except Exception as fallback_error:
            logger.error(f"Fallback failed: {fallback_error}")
            raise ImportError("Both official and custom model loading failed")
    
    except Exception as e:
        logger.error(f"Failed to load official model: {e}")
        raise

__all__ = ['load_tmtb_model']
