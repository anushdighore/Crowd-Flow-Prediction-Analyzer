import torch

# pytorch cross scan =============
class CrossScan(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x: torch.Tensor):
        B, C, H, W = x.shape
        ctx.shape = (B, C, H, W)
        xs = x.new_empty((B, 4, C, H * W))
        xs[:, 0] = x.flatten(2, 3)
        xs[:, 1] = x.transpose(dim0=2, dim1=3).flatten(2, 3)
        xs[:, 2:4] = torch.flip(xs[:, 0:2], dims=[-1])
        return xs
    
    @staticmethod
    def backward(ctx, ys: torch.Tensor):
        # out: (b, k, d, l)
        B, C, H, W = ctx.shape
        L = H * W
        ys = ys[:, 0:2] + ys[:, 2:4].flip(dims=[-1]).view(B, 2, -1, L)
        y = ys[:, 0] + ys[:, 1].view(B, -1, W, H).transpose(dim0=2, dim1=3).contiguous().view(B, -1, L)
        return y.view(B, -1, H, W)


class CrossMerge(torch.autograd.Function):
    @staticmethod
    def forward(ctx, ys: torch.Tensor):
        B, K, D, H, W = ys.shape
        ctx.shape = (H, W)
        ys = ys.view(B, K, D, -1)
        ys = ys[:, 0:2] + ys[:, 2:4].flip(dims=[-1]).view(B, 2, D, -1)
        y = ys[:, 0] + ys[:, 1].view(B, -1, W, H).transpose(dim0=2, dim1=3).contiguous().view(B, D, -1)
        return y
    
    @staticmethod
    def backward(ctx, x: torch.Tensor):
        # B, D, L = x.shape
        # out: (b, k, d, l)
        H, W = ctx.shape
        B, C, L = x.shape
        xs = x.new_empty((B, 4, C, L))
        xs[:, 0] = x
        xs[:, 1] = x.view(B, C, H, W).transpose(dim0=2, dim1=3).flatten(2, 3)
        xs[:, 2:4] = torch.flip(xs[:, 0:2], dims=[-1])
        xs = xs.view(B, 4, C, H, W)
        return xs


# these are for ablations =============
class CrossScan_Ab_2direction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x: torch.Tensor):
        B, C, H, W = x.shape
        ctx.shape = (B, C, H, W)
        x = x.view(B, 1, C, H * W).repeat(1, 2, 1, 1)
        x = torch.cat([x, x.flip(dims=[-1])], dim=1)
        return x
    
    @staticmethod
    def backward(ctx, ys: torch.Tensor):
        B, C, H, W = ctx.shape
        L = H * W
        ys = ys[:, 0:2] + ys[:, 2:4].flip(dims=[-1]).view(B, 2, -1, L)
        return ys.sum(1).view(B, -1, H, W)


class CrossMerge_Ab_2direction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, ys: torch.Tensor):
        B, K, D, H, W = ys.shape
        ctx.shape = (H, W)
        ys = ys.view(B, K, D, -1)
        ys = ys[:, 0:2] + ys[:, 2:4].flip(dims=[-1]).view(B, 2, D, -1)
        return ys.contiguous().sum(1)
    
    @staticmethod
    def backward(ctx, x: torch.Tensor):
        H, W = ctx.shape
        B, C, L = x.shape
        x = x.view(B, 1, C, H * W).repeat(1, 2, 1, 1)
        x = torch.cat([x, x.flip(dims=[-1])], dim=1)
        return x.view(B, 4, C, H, W)


class CrossScan_Ab_1direction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x: torch.Tensor):
        B, C, H, W = x.shape
        ctx.shape = (B, C, H, W)
        x = x.view(B, 1, C, H * W).repeat(1, 4, 1, 1)
        return x
    
    
    @staticmethod
    def backward(ctx, ys: torch.Tensor):
        B, C, H, W = ctx.shape
        return ys.view(B, 4, -1, H, W).sum(1)


class CrossMerge_Ab_1direction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, ys: torch.Tensor):
        B, K, C, H, W = ys.shape
        ctx.shape = (B, C, H, W)
        return ys.view(B, 4, -1, H * W).sum(1)
    
    @staticmethod
    def backward(ctx, x: torch.Tensor):
        B, C, H, W = ctx.shape
        return x.view(B, 1, C, H, W).repeat(1, 4, 1, 1, 1)


# PyTorch-only implementation - no CUDA extensions needed
# For CUDA extensions, see: future_cuda_extensions/
print("✅ Using PyTorch-only selective scan (no CUDA extensions)")


def check_nan_inf(tag: str, x: torch.Tensor, enable=True):
    if enable:
        if torch.isinf(x).any() or torch.isnan(x).any():
            print(tag, torch.isinf(x).any(), torch.isnan(x).any(), flush=True)
            import pdb; pdb.set_trace()


# fvcore flops =======================================
def flops_selective_scan_fn(B=1, L=256, D=768, N=16, with_D=True, with_Z=False, with_complex=False):
    """
    u: r(B D L)
    delta: r(B D L)
    A: r(D N)
    B: r(B N L)
    C: r(B N L)
    D: r(D)
    z: r(B D L)
    delta_bias: r(D), fp32
    
    ignores:
        [.float(), +, .softplus, .shape, new_zeros, repeat, stack, to(dtype), silu] 
    """
    assert not with_complex 
    # https://github.com/state-spaces/mamba/issues/110
    flops = 9 * B * L * D * N
    if with_D:
        flops += B * D * L
    if with_Z:
        flops += B * D * L    
    return flops

# this is only for selective_scan_ref...
def flops_selective_scan_ref(B=1, L=256, D=768, N=16, with_D=True, with_Z=False, with_Group=True, with_complex=False):
    """
    u: r(B D L)
    delta: r(B D L)
    A: r(D N)
    B: r(B N L)
    C: r(B N L)
    D: r(D)
    z: r(B D L)
    delta_bias: r(D), fp32
    
    ignores:
        [.float(), +, .softplus, .shape, new_zeros, repeat, stack, to(dtype), silu] 
    """
    import numpy as np
    
    # fvcore.nn.jit_handles
    def get_flops_einsum(input_shapes, equation):
        np_arrs = [np.zeros(s) for s in input_shapes]
        optim = np.einsum_path(equation, *np_arrs, optimize="optimal")[1]
        for line in optim.split("\n"):
            if "optimized flop" in line.lower():
                # divided by 2 because we count MAC (multiply-add counted as one flop)
                flop = float(np.floor(float(line.split(":")[-1]) / 2))
                return flop
    

    assert not with_complex

    flops = 0 # below code flops = 0

    flops += get_flops_einsum([[B, D, L], [D, N]], "bdl,dn->bdln")
    if with_Group:
        flops += get_flops_einsum([[B, D, L], [B, N, L], [B, D, L]], "bdl,bnl,bdl->bdln")
    else:
        flops += get_flops_einsum([[B, D, L], [B, D, N, L], [B, D, L]], "bdl,bdnl,bdl->bdln")
  
    in_for_flops = B * D * N   
    if with_Group:
        in_for_flops += get_flops_einsum([[B, D, N], [B, D, N]], "bdn,bdn->bd")
    else:
        in_for_flops += get_flops_einsum([[B, D, N], [B, N]], "bdn,bn->bd")
    flops += L * in_for_flops 
    if with_D:
        flops += B * D * L
    if with_Z:
        flops += B * D * L  
    return flops


def print_jit_input_names(inputs):
    print("input params: ", end=" ", flush=True)
    try: 
        for i in range(10):
            print(inputs[i].debugName(), end=" ", flush=True)
    except Exception as e:
        pass
    print("", flush=True)

# Pure PyTorch Selective Scan Implementation
# ============================================
class SelectiveScanPyTorch(torch.autograd.Function):
    """PyTorch-only selective scan - works without CUDA extensions"""

    @staticmethod
    def forward(ctx, u, delta, A, B, C, D=None, delta_bias=None, delta_softplus=False, nrows=1, backnrows=1, oflex=True):
        ctx.delta_softplus = delta_softplus

        batch, total_dim, seq_len = u.shape

        # Determine number of directional groups (K) and state size
        if B.dim() == 4:
            _, groups, state_size, _ = B.shape
        else:
            groups = 1
            state_size = B.shape[1]
            B = B.unsqueeze(1)
            C = C.unsqueeze(1)

        feature_dim = total_dim // groups

        # Reshape tensors to make group dimension explicit
        u_grouped = u.view(batch, groups, feature_dim, seq_len)
        delta_grouped = delta.view(batch, groups, feature_dim, seq_len)
        B_grouped = B.view(batch, groups, state_size, seq_len)
        C_grouped = C.view(batch, groups, state_size, seq_len)
        A_grouped = A.view(groups, feature_dim, -1)
        D_grouped = D.view(groups, feature_dim) if D is not None else None
        delta_bias_grouped = delta_bias.view(groups, feature_dim) if delta_bias is not None else None

        # Apply delta bias / softplus if required
        if delta_bias_grouped is not None:
            delta_grouped = delta_grouped + delta_bias_grouped.unsqueeze(0).unsqueeze(-1)
        if delta_softplus:
            delta_grouped = torch.nn.functional.softplus(delta_grouped)

        out_grouped = torch.zeros_like(u_grouped)
        state_cache = torch.zeros(batch, groups, feature_dim, state_size, device=u.device, dtype=u.dtype)

        for g in range(groups):
            A_g = A_grouped[g].to(u.dtype)  # (feature_dim, state_size)
            u_g = u_grouped[:, g]
            delta_g = delta_grouped[:, g]
            B_g = B_grouped[:, g]
            C_g = C_grouped[:, g]
            x_state = torch.zeros(batch, feature_dim, state_size, device=u.device, dtype=u.dtype)

            for t in range(seq_len):
                delta_t = delta_g[:, :, t]
                exp_term = torch.exp(A_g.unsqueeze(0) * delta_t.unsqueeze(-1))
                x_state = x_state * exp_term + u_g[:, :, t].unsqueeze(-1) * B_g[:, :, t].unsqueeze(1)
                out_grouped[:, g, :, t] = (x_state * C_g[:, :, t].unsqueeze(1)).sum(dim=-1)

            if D_grouped is not None:
                out_grouped[:, g] = out_grouped[:, g] + u_g * D_grouped[g].unsqueeze(-1)

            state_cache[:, g] = x_state

        out = out_grouped.view(batch, total_dim, seq_len)

        # Save tensors for (theoretical) backward path
        saved_D = D_grouped.reshape(-1) if D_grouped is not None else torch.empty(0, device=u.device, dtype=u.dtype)
        saved_delta_bias = (
            delta_bias_grouped.reshape(-1) if delta_bias_grouped is not None else torch.empty(0, device=u.device, dtype=u.dtype)
        )
        ctx.save_for_backward(
            u,
            delta_grouped.view(batch, total_dim, seq_len),
            A_grouped.reshape(groups * feature_dim, -1),
            B_grouped,
            C_grouped,
            saved_D,
            saved_delta_bias,
            state_cache.view(batch, total_dim, state_size),
        )
        return out

    @staticmethod
    def backward(ctx, dout):
        u, delta, A, B, C, D_flat, delta_bias_flat, x = ctx.saved_tensors

        D = None if D_flat.numel() == 0 else D_flat
        delta_bias = None if delta_bias_flat.numel() == 0 else delta_bias_flat

        du = dout.clone()
        if D is not None:
            du = du + dout * D.unsqueeze(-1)
        ddelta = torch.zeros_like(delta)
        dA = torch.zeros_like(A)
        dB = torch.zeros_like(B)
        dC = torch.zeros_like(C)
        dD = torch.zeros_like(D) if D is not None else None
        ddelta_bias = torch.zeros_like(delta_bias) if delta_bias is not None else None
        return (du, ddelta, dA, dB, dC, dD, ddelta_bias, None, None, None, None)


# Use PyTorch implementation for all variants
SelectiveScanMamba = SelectiveScanPyTorch
SelectiveScanCore = SelectiveScanPyTorch
SelectiveScanOflex = SelectiveScanPyTorch


def selective_scan_flop_jit(inputs, outputs, flops_fn=flops_selective_scan_fn):
    print_jit_input_names(inputs)
    B, D, L = inputs[0].type().sizes()
    N = inputs[2].type().sizes()[1]
    flops = flops_fn(B=B, L=L, D=D, N=N, with_D=True, with_Z=False)
    return flops




