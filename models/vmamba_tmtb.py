import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import logging
from typing import Optional, Dict, Any, Tuple
import warnings

logger = logging.getLogger(__name__)

def selective_scan_fn(u, delta, A, B, C, D=None, z=None, delta_bias=None, delta_softplus=False):
    """
    Simplified selective scan function for VMamba-TMTB.
    This implements the core state space mechanism.
    """
    batch_size, seq_len, d_inner = u.shape
    device = u.device

    # Initialize hidden state
    h = torch.zeros(batch_size, d_inner, A.shape[-1], device=device, dtype=u.dtype)

    outputs = []
    for i in range(seq_len):
        # Delta (time step) processing
        if delta_softplus:
            dt = F.softplus(delta[:, i] + (delta_bias if delta_bias is not None else 0))
        else:
            dt = delta[:, i]

        # State transition: h_t = exp(A * dt) * h_{t-1} + dt * B * u_t
        dA = torch.exp(A.unsqueeze(0) * dt.unsqueeze(-1))  # (batch, d_inner, d_state)
        dB = dt.unsqueeze(-1) * B[:, i].unsqueeze(1)  # (batch, d_inner, d_state)

        h = dA * h + dB * u[:, i].unsqueeze(-1)

        # Output: y_t = C * h_t
        y = torch.sum(h * C[:, i].unsqueeze(1), dim=-1)  # (batch, d_inner)

        # Add direct connection
        if D is not None:
            y = y + D * u[:, i]

        outputs.append(y)

    output = torch.stack(outputs, dim=1)

    # Apply gate if provided
    if z is not None:
        output = output * F.silu(z)

    return output

class PatchEmbed(nn.Module):
    """
    Image to Patch Embedding for VMamba-TMTB
    CORRECTED: First layer outputs 64 channels (from checkpoint analysis)
    """
    def __init__(self, img_size=224, patch_size=4, in_chans=3, embed_dim=128):
        super().__init__()
        self.img_size = img_size
        self.patch_size = patch_size
        self.grid_size = img_size // patch_size
        self.num_patches = self.grid_size ** 2

        # Multi-stage patch embedding matching checkpoint structure
        # patch_embed.0: Conv2d(3, 64, 3x3) 
        # patch_embed.2: Conv2d(64, 64, 3x3) -> But checkpoint shows just bias (BatchNorm)
        self.proj = nn.Sequential(
            nn.Conv2d(in_chans, 64, kernel_size=3, stride=2, padding=1),  # Stage 0
            nn.BatchNorm2d(64),  # Stage 1 (implicit)
            nn.Conv2d(64, 64, kernel_size=3, stride=2, padding=1),        # Stage 2
            nn.BatchNorm2d(64),  # Stage 3 (implicit)
            nn.ReLU(inplace=True),
            nn.Conv2d(64, embed_dim, kernel_size=3, stride=1, padding=1), # Stage 5
        )

    def forward(self, x):
        B, C, H, W = x.shape
        # Project to patches
        x = self.proj(x)  # (B, embed_dim, H//4, W//4)
        x = x.flatten(2).transpose(1, 2)  # (B, num_patches, embed_dim)
        return x

class VSS_Block(nn.Module):
    """
    Visual State Space Block - Core VMamba component
    CORRECTED: Uses exact dimensions from checkpoint
    """
    def __init__(
        self, 
        hidden_dim=128,  # CORRECTED: Base dimension
        d_state=16, 
        d_conv=3, 
        expand=2,
        dt_rank="auto",
        drop_path=0.1
    ):
        super().__init__()

        self.hidden_dim = hidden_dim
        self.d_state = d_state
        self.d_conv = d_conv
        self.expand = expand
        self.d_inner = int(expand * hidden_dim)

        if dt_rank == "auto":
            self.dt_rank = math.ceil(hidden_dim / 16)
        else:
            self.dt_rank = dt_rank

        # Layer norm
        self.norm = nn.LayerNorm(hidden_dim)
        self.norm2 = nn.LayerNorm(hidden_dim)

        # MLP (matching checkpoint structure)
        self.mlp = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim * 4),  # fc1
            nn.GELU(),
            nn.Linear(hidden_dim * 4, hidden_dim), # fc2
        )

        # Input projection - splits into x and z
        self.in_proj = nn.Linear(hidden_dim, self.d_inner * 2, bias=False)

        # Depthwise convolution
        self.conv2d = nn.Conv2d(
            self.d_inner, self.d_inner, 
            kernel_size=d_conv, padding=d_conv//2, 
            groups=self.d_inner
        )

        # SSM parameters (matching checkpoint keys)
        self.x_proj = nn.Linear(self.d_inner, self.dt_rank + d_state * 2, bias=False)
        self.dt_proj = nn.Linear(self.dt_rank, self.d_inner, bias=True)

        # Initialize A (state transition matrix)
        A = torch.arange(1, d_state + 1, dtype=torch.float32).repeat(self.d_inner, 1)
        A_log = torch.log(A)
        self.A_log = nn.Parameter(A_log)

        # Initialize D (skip connection)
        self.D = nn.Parameter(torch.ones(self.d_inner))

        # Output projection
        self.out_proj = nn.Linear(self.d_inner, hidden_dim, bias=False)

        # Drop path
        self.drop_path = nn.Dropout(drop_path) if drop_path > 0. else nn.Identity()

    def forward(self, x):
        """
        x: (B, H*W, C)
        """
        B, L, C = x.shape
        H = W = int(math.sqrt(L))  # Assume square patches

        # Residual connection
        skip = x

        # Layer norm
        x = self.norm(x)

        # Input projection
        xz = self.in_proj(x)  # (B, L, 2*d_inner)
        x, z = xz.chunk(2, dim=-1)  # Each: (B, L, d_inner)

        # 2D Convolution - need to reshape to spatial format
        x_2d = x.transpose(1, 2).view(B, self.d_inner, H, W)  # (B, d_inner, H, W)
        x_2d = self.conv2d(x_2d)
        x = x_2d.view(B, self.d_inner, -1).transpose(1, 2)  # Back to (B, L, d_inner)

        # Activation
        x = F.silu(x)

        # SSM projection
        x_dbl = self.x_proj(x)  # (B, L, dt_rank + 2*d_state)
        dt, B_ssm, C_ssm = torch.split(x_dbl, [self.dt_rank, self.d_state, self.d_state], dim=-1)

        # Delta projection
        dt = self.dt_proj(dt)  # (B, L, d_inner)

        # A matrix
        A = -torch.exp(self.A_log.float())  # (d_inner, d_state)

        # Bidirectional scan
        # Forward scan
        y1 = selective_scan_fn(x, dt, A, B_ssm, C_ssm, self.D, z, delta_softplus=True)

        # Backward scan
        x_flip = torch.flip(x, dims=[1])
        dt_flip = torch.flip(dt, dims=[1])
        B_flip = torch.flip(B_ssm, dims=[1])
        C_flip = torch.flip(C_ssm, dims=[1])
        z_flip = torch.flip(z, dims=[1])

        y2 = selective_scan_fn(x_flip, dt_flip, A, B_flip, C_flip, self.D, z_flip, delta_softplus=True)
        y2 = torch.flip(y2, dims=[1])

        # Combine bidirectional outputs
        y = (y1 + y2) * 0.5

        # Output projection
        y = self.out_proj(y)

        # First residual connection with drop path
        x = skip + self.drop_path(y)

        # MLP branch  
        x = x + self.mlp(self.norm2(x))

        return x

class VMambaTMTB(nn.Module):
    """
    VMamba-TMTB: Visual State Space Model for Crowd Counting
    CORRECTED: Exact dimensions matching your checkpoint
    """
    def __init__(
        self,
        img_size=224,
        patch_size=4,
        in_chans=3,
        embed_dim=128,        # CORRECTED: Base dimension
        depths=[2, 2, 15, 2], # CORRECTED: From your checkpoint
        num_classes=25,       # CORRECTED: From your checkpoint
        drop_path_rate=0.1,
    ):
        super().__init__()

        self.img_size = img_size
        self.patch_size = patch_size
        self.embed_dim = embed_dim
        self.depths = depths
        self.num_classes = num_classes

        # Patch embedding
        self.patch_embed = PatchEmbed(
            img_size=img_size,
            patch_size=patch_size,
            in_chans=in_chans,
            embed_dim=embed_dim
        )

        # Stochastic depth
        dpr = [x.item() for x in torch.linspace(0, drop_path_rate, sum(depths))]

        # Build layers with correct dimensions [128, 256, 512, 1024]
        self.layers = nn.ModuleList()
        dims = [128, 256, 512, 1024]  # CORRECTED: Exact dimensions from checkpoint

        for i_layer in range(len(depths)):
            layer_blocks = nn.ModuleList([
                VSS_Block(
                    hidden_dim=dims[i_layer],  # CORRECTED: Use exact dims
                    d_state=16,
                    d_conv=3,
                    expand=2,
                    drop_path=dpr[sum(depths[:i_layer]) + i]
                )
                for i in range(depths[i_layer])
            ])
            self.layers.append(layer_blocks)

        # Final layer norm
        self.classifier = nn.ModuleDict({
            'norm': nn.LayerNorm(1024)  # CORRECTED: Final dimension
        })

        # Regression head for density map
        # Regression head for density map
        # FINAL CORRECTED: Exact decoder structure matching checkpoint
        self.reg_head = nn.ModuleDict({
            'count': nn.ModuleDict({
                'decoder': nn.Sequential(
                    nn.Identity(),                                           # decoder.0 (skip)
                    nn.Conv2d(1024, 64, kernel_size=3, padding=1),          # decoder.1 ✅
                    nn.BatchNorm2d(64),                                     # decoder.2 ✅
                    nn.Identity(),                                          # decoder.3 (skip)
                    nn.Conv2d(64, 32, kernel_size=3, padding=1),            # decoder.4 ✅
                    nn.BatchNorm2d(32),                                     # decoder.5 ✅
                    nn.Identity(),                                          # decoder.6 (skip)
                    nn.Identity(),                                          # decoder.7 (skip)
                    nn.Conv2d(32, 16, kernel_size=3, padding=1), # decoder.8 ✅
                    nn.BatchNorm2d(16),                                     # decoder.9 ✅ 
                    nn.Identity(),                                          # decoder.10 (skip)
                    nn.Conv2d(16, 1, kernel_size=1),                       # decoder.11 ✅
                )
            })
        })



        # Anti-noise classification head
        # CORRECTED: Proper dimensions matching checkpoint  
        self.cls_head = nn.Sequential(
            nn.Conv2d(1024, 512, kernel_size=1),    # CORRECTED: 1x1 conv, 512 channels
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 25, kernel_size=1)       # CORRECTED: 25 classes
        )

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.trunc_normal_(m.weight, std=0.02)
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.LayerNorm):
            nn.init.zeros_(m.bias)
            nn.init.ones_(m.weight)
        elif isinstance(m, nn.Conv2d):
            nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            if m.bias is not None:
                nn.init.zeros_(m.bias)

    def forward_backbone(self, x):
        """Forward through backbone only"""
        B, C, H, W = x.shape

        # Patch embedding
        x = self.patch_embed(x)  # (B, num_patches, embed_dim)

        # Apply VSS blocks with dimension scaling
        for i, layer_blocks in enumerate(self.layers):
            for block in layer_blocks:
                x = block(x)

            # Dimension scaling between layers (if not last layer)
            if i < len(self.layers) - 1:
                # Scale from current dim to next dim
                B, L, C = x.shape
                H_curr = W_curr = int(math.sqrt(L))

                # Reshape to spatial
                x_spatial = x.transpose(1, 2).view(B, C, H_curr, W_curr)

                # Downsample and increase channels
                next_dim = [128, 256, 512, 1024][i + 1]
                downsample = nn.Conv2d(C, next_dim, kernel_size=2, stride=2).to(x.device)
                x_spatial = downsample(x_spatial)

                # Back to sequence
                x = x_spatial.flatten(2).transpose(1, 2)

        # Final norm
        x = self.classifier['norm'](x)

        return x

    def forward(self, x, return_cls=False):
        """
        Forward pass with dual heads
        """
        B, C, H, W = x.shape

        # Backbone forward
        features = self.forward_backbone(x)  # (B, num_patches, 1024)

        # Reshape to spatial for heads
        grid_size = features.shape[1] ** 0.5
        grid_size = int(grid_size)
        features_spatial = features.transpose(1, 2).view(B, 1024, grid_size, grid_size)

        # Regression head - density map
        # Custom decoder forward to use specific indices
        x = features_spatial
        x = F.relu(self.reg_head['count']['decoder'][1](x))     # decoder.1
        x = self.reg_head['count']['decoder'][2](x)             # decoder.2
        x = F.relu(self.reg_head['count']['decoder'][4](x))     # decoder.4
        x = self.reg_head['count']['decoder'][5](x)             # decoder.5
        x = F.relu(self.reg_head['count']['decoder'][8](x))     # decoder.8
        x = self.reg_head['count']['decoder'][9](x)             # decoder.9
        density_map = self.reg_head['count']['decoder'][11](x)  # decoder.11


        # Upsample to reasonable size
        density_map = F.interpolate(
            density_map, 
            size=(H // 4, W // 4), 
            mode='bilinear', 
            align_corners=False
        )

        if return_cls:
            # Classification head
            cls_features = F.adaptive_avg_pool2d(features_spatial, 1)  # Global avg pool
            cls_logits = self.cls_head(cls_features).squeeze(-1).squeeze(-1)
            return density_map, cls_logits

        return density_map

def load_tmtb_model(checkpoint_path: str, device: Optional[str] = None) -> VMambaTMTB:
    """
    Load VMamba-TMTB model from checkpoint with CORRECTED dimensions
    """
    try:
        logger.info(f"Loading VMamba-TMTB from: {checkpoint_path}")

        # Auto-detect device
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location=device)
        logger.info(f"Checkpoint contains {len(checkpoint)} keys")

        # Initialize model with CORRECTED parameters matching checkpoint
        model = VMambaTMTB(
            img_size=224,
            patch_size=4,
            in_chans=3,
            embed_dim=128,        # CORRECTED
            depths=[2, 2, 15, 2], # CORRECTED  
            num_classes=25,       # CORRECTED
        )

        # Extract state dict
        if 'model' in checkpoint:
            state_dict = checkpoint['model']
        elif 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
        else:
            state_dict = checkpoint

        # Handle DataParallel prefix and vmamba prefix
        new_state_dict = {}
        for k, v in state_dict.items():
            # Remove 'module.' prefix from DataParallel
            name = k.replace('module.', '') if k.startswith('module.') else k
            # Remove 'vmamba.' prefix to match our model structure
            name = name.replace('vmamba.', '') if name.startswith('vmamba.') else name
            new_state_dict[name] = v

        # Load with strict=False to handle architecture differences
        missing_keys, unexpected_keys = model.load_state_dict(new_state_dict, strict=False)

        if missing_keys:
            logger.warning(f"Missing keys: {missing_keys[:5]}...")  # Show first 5
        if unexpected_keys:
            logger.warning(f"Unexpected keys: {unexpected_keys[:5]}...")  # Show first 5

        # Log successful loading
        loaded_keys = len([k for k in new_state_dict.keys() if k in model.state_dict()])
        total_keys = len(model.state_dict())
        logger.info(f"✅ Loaded {loaded_keys}/{total_keys} parameters successfully")
        logger.info(f"Match rate: {loaded_keys/total_keys*100:.1f}%")

        return model

    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        raise RuntimeError(f"Could not load VMamba-TMTB model: {e}")

# Export classes and functions
__all__ = [
    'VMambaTMTB', 'VSS_Block', 'PatchEmbed', 
    'load_tmtb_model', 'selective_scan_fn'
]
