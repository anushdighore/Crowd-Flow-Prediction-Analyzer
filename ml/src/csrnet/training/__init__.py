"""
CSRNet Training Module
Fine-tuning pipeline for CSRNet on ShanghaiTech Part A
"""

__version__ = "1.0.0"

from .dataset import ShanghaiTechDataset, ShanghaiTechPartA
from .train import CSRNetTrainer
from .evaluate import CSRNetEvaluator

__all__ = [
    'ShanghaiTechDataset',
    'ShanghaiTechPartA',
    'CSRNetTrainer',
    'CSRNetEvaluator'
]
