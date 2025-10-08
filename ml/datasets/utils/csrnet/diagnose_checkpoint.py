"""
CSRNet Checkpoint Diagnostic Script
Run this to check your checkpoint file and identify issues
"""
import torch
import sys

def diagnose_checkpoint(checkpoint_path):
    """Diagnose CSRNet checkpoint file"""
    print("=" * 60)
    print("🔍 CSRNet Checkpoint Diagnostic")
    print("=" * 60)
    
    try:
        # Load checkpoint
        print(f"\n📂 Loading checkpoint: {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        print("✅ Checkpoint loaded successfully\n")
        
        # Check checkpoint structure
        print("📊 Checkpoint Structure:")
        print(f"   Type: {type(checkpoint)}")
        
        if isinstance(checkpoint, dict):
            print(f"\n🔑 Keys in checkpoint:")
            for key in checkpoint.keys():
                print(f"   - {key}")
            
            # Check for state_dict
            if 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
                print("\n   ✅ Found 'state_dict' key")
            elif 'model' in checkpoint:
                state_dict = checkpoint['model']
                print("\n   ✅ Found 'model' key")
            else:
                state_dict = checkpoint
                print("\n   ⚠️  Using checkpoint directly as state_dict")
        else:
            state_dict = checkpoint
            print("   ⚠️  Checkpoint is not a dict, using directly")
        
        # Analyze state dict
        print("\n🏗️  Model Architecture Analysis:")
        print(f"   Total parameters: {len(state_dict)}")
        
        print("\n📋 Layer Names (first 10):")
        for i, key in enumerate(list(state_dict.keys())[:10]):
            shape = state_dict[key].shape if hasattr(state_dict[key], 'shape') else 'N/A'
            print(f"   {i+1}. {key}: {shape}")
        
        print("\n📋 Layer Names (last 5):")
        for i, key in enumerate(list(state_dict.keys())[-5:]):
            shape = state_dict[key].shape if hasattr(state_dict[key], 'shape') else 'N/A'
            print(f"   {i+1}. {key}: {shape}")
        
        # Check for common layer patterns
        print("\n🔍 Checking Layer Patterns:")
        has_frontend = any('frontend' in k for k in state_dict.keys())
        has_backend = any('backend' in k for k in state_dict.keys())
        has_output = any('output' in k for k in state_dict.keys())
        has_module = any('module.' in k for k in state_dict.keys())
        
        print(f"   Frontend layers: {'✅' if has_frontend else '❌'}")
        print(f"   Backend layers: {'✅' if has_backend else '❌'}")
        print(f"   Output layer: {'✅' if has_output else '❌'}")
        print(f"   'module.' prefix: {'✅' if has_module else '❌'}")
        
        # Check for numbered layers (vanilla pattern)
        has_numbered = any(k.split('.')[0].isdigit() for k in state_dict.keys())
        print(f"   Numbered layers (0.weight, 1.weight, etc.): {'✅' if has_numbered else '❌'}")
        
        # Recommendations
        print("\n💡 Recommendations:")
        if has_module:
            print("   ⚠️  Checkpoint has 'module.' prefix (trained with DataParallel)")
            print("   → Need to remove 'module.' prefix when loading")
        
        if has_numbered and not (has_frontend or has_backend):
            print("   ⚠️  Checkpoint uses numbered layers (vanilla PyTorch)")
            print("   → Need to map to frontend/backend/output_layer")
        
        if not has_output:
            print("   ⚠️  No output layer found")
            print("   → May need custom loading logic")
        
        print("\n" + "=" * 60)
        return state_dict
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    checkpoint_path = "D:\College\Major Project\checkpoints\csrnet.pth"
    if len(sys.argv) > 1:
        checkpoint_path = sys.argv[1]
    
    diagnose_checkpoint(checkpoint_path)
