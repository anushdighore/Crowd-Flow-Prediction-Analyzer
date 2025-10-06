from typing import Optional, Dict, Any

import torch
import torch.nn as nn
from timm.models.layers import trunc_normal_
from .vmamba import *
from .counting_head import CountingHead


class MAMBA4CC(nn.Module):
    def __init__(self, vmamba_path: Optional[str] = None, num_classes: int = 25, strict_backbone: bool = True):
        super().__init__()
        self.vmamba = VSSM(
            depths=[2, 2, 15, 2],
            dims=128,
            drop_path_rate=0.6,
            # ===================
            ssm_d_state=1,
            ssm_ratio=2.0,
            ssm_dt_rank="auto",
            ssm_conv=3,
            ssm_conv_bias=False,
            forward_type="v3noz",
            # ===================
            mlp_ratio=4.0,
            # ===================
            downsample_version="v3",
            patchembed_version="v2",
            # norm_layer="ln2d",
        )
        if vmamba_path:
            checkpoint = torch.load(vmamba_path, map_location="cpu", weights_only=False)
            if isinstance(checkpoint, dict):
                state_dict: Dict[str, Any]
                if "model" in checkpoint:
                    state_dict = checkpoint["model"]
                elif "state_dict" in checkpoint:
                    state_dict = checkpoint["state_dict"]
                else:
                    state_dict = {
                        key.split("vmamba.", 1)[1] if key.startswith("vmamba.") else key: value
                        for key, value in checkpoint.items()
                        if isinstance(value, torch.Tensor) and key.startswith("vmamba.")
                    }
                self.vmamba.load_state_dict(state_dict, strict=strict_backbone)
            else:
                self.vmamba.load_state_dict(checkpoint, strict=strict_backbone)
        _NORMLAYERS = dict(
            ln=nn.LayerNorm,
            ln2d=LayerNorm2d,
            bn=nn.BatchNorm2d,
        )
        norm_layer: nn.Module = _NORMLAYERS.get("LN".lower(), None)

        self.vmamba.classifier = nn.Sequential(
            OrderedDict(
                norm=norm_layer(self.vmamba.num_features),  # B,H,W,C
                permute=(
                    Permute(0, 3, 1, 2)
                    if not self.vmamba.channel_first
                    else nn.Identity()
                ),
            )
        )
        self.vmamba.classifier.apply(self._init_weights)

        self.cls_head = nn.Sequential(
            OrderedDict(
                upsample=nn.Upsample(
                    scale_factor=4, mode="bilinear", align_corners=False
                ),
                conv1=nn.Conv2d(self.vmamba.num_features, 512, 1, 1),
                relu1=nn.ReLU(inplace=True),
                conv2=nn.Conv2d(512, num_classes, 1, 1),
            )
        )
        self.reg_head = nn.Sequential(
            OrderedDict(
                count=CountingHead(self.vmamba.num_features, 1),
            )
        )
        self.cls_head.apply(self._init_weights)
        self.reg_head.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            trunc_normal_(m.weight, std=0.02)
            if isinstance(m, nn.Linear) and m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.LayerNorm):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)
        elif isinstance(m, nn.Conv2d):
            nn.init.normal_(m.weight, std=0.01)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.BatchNorm2d):
            m.weight.data.fill_(1.0)
            m.bias.data.zero_()

    def forward(self, x):
        x = self.vmamba(x)
        cls_score = self.cls_head(x)
        pred_den = self.reg_head(x)
        cls_score_max = cls_score.max(dim=1, keepdim=True)[0]
        cls_score = cls_score - cls_score_max
        return pred_den, cls_score


def mamba(num_classes: int = 25, vmamba_path: Optional[str] = None, strict_backbone: bool = True):
    model = MAMBA4CC(vmamba_path=vmamba_path, num_classes=num_classes, strict_backbone=strict_backbone)
    return model
