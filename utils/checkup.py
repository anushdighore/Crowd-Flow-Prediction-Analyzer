import torch
import re

def analyze_checkpoint_structure():
    checkpoint_path = "../checkpoints/jhu_5.pth"
    
    try:
        ckpt = torch.load(checkpoint_path, map_location="cpu")
        state_dict = ckpt.get('state_dict', ckpt.get('model', ckpt)) if isinstance(ckpt, dict) else ckpt
        
        print("🔍 DETAILED CHECKPOINT ANALYSIS:")
        print("="*60)
        
        # Group keys by component
        components = {
            'patch_embed': [],
            'vmamba_layers': [],
            'classifier': [],
            'reg_head': [],
            'cls_head': [],
            'other': []
        }
        
        layer_structure = {}
        total_params = 0
        
        for key, value in state_dict.items():
            if torch.is_tensor(value):
                params = value.numel()
                total_params += params
                shape = list(value.shape)
                
                # Categorize keys
                if 'patch_embed' in key:
                    components['patch_embed'].append((key, shape, params))
                elif 'vmamba.layers' in key:
                    components['vmamba_layers'].append((key, shape, params))
                elif 'classifier' in key:
                    components['classifier'].append((key, shape, params))
                elif 'reg_head' in key:
                    components['reg_head'].append((key, shape, params))
                elif 'cls_head' in key:
                    components['cls_head'].append((key, shape, params))
                else:
                    components['other'].append((key, shape, params))
                
                # Extract layer structure
                if 'vmamba.layers' in key:
                    parts = key.split('.')
                    if len(parts) >= 5 and parts[4].isdigit():
                        layer_idx = int(parts[2])
                        block_idx = int(parts[4])
                        if layer_idx not in layer_structure:
                            layer_structure[layer_idx] = set()
                        layer_structure[layer_idx].add(block_idx)
        
        print(f"📊 TOTAL PARAMETERS: {total_params:,}")
        print()
        
        # Analyze each component  
        for comp_name, items in components.items():
            if items:
                comp_params = sum(params for _, _, params in items)
                print(f"🔧 {comp_name.upper()}:")
                print(f"   Total parameters: {comp_params:,}")
                print(f"   Layers: {len(items)}")
                
                # Show key examples
                for key, shape, params in sorted(items)[:3]:
                    print(f"   • {key}: {shape} ({params:,} params)")
                if len(items) > 3:
                    print(f"   ... and {len(items)-3} more layers")
                print()
        
        # Determine exact depths
        print("🏗️ LAYER STRUCTURE:")
        depths = []
        for layer_idx in sorted(layer_structure.keys()):
            max_block = max(layer_structure[layer_idx]) if layer_structure[layer_idx] else 0
            depth = max_block + 1
            depths.append(depth)
            print(f"   Layer {layer_idx}: {depth} blocks (blocks 0-{max_block})")
        
        print(f"\n🎯 EXACT DEPTHS: {depths}")
        
        # Find dimension info from norm layers
        dims = []
        for key, shape, _ in components['vmamba_layers']:
            if 'blocks.0.norm.weight' in key:
                layer_match = re.search(r'layers\.(\d+)', key)
                if layer_match:
                    layer_idx = int(layer_match.group(1))
                    while len(dims) <= layer_idx:
                        dims.append(0)
                    dims[layer_idx] = shape[0]
        
        dims = [d for d in dims if d > 0]
        if dims:
            print(f"🎯 EXACT DIMENSIONS: {dims}")
        
        print(f"\n📋 EXACT CONFIG NEEDED:")
        if depths:
            print(f"depths = {depths}")
        if dims:
            print(f"embed_dim = {dims[0] if dims else 128}")
            print(f"stage_dims = {dims}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_checkpoint_structure()
