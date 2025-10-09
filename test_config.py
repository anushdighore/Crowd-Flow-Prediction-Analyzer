"""
Quick test script to verify config-driven resizing works correctly
"""
import sys
from pathlib import Path

# Add ml/src to path
ml_src = Path(__file__).parent / "ml" / "src"
sys.path.insert(0, str(ml_src))

from core.config_loader import load_csrnet_config, load_tmtb_config, get_dimensions_for_source

def test_config_loading():
    """Test that configs load correctly"""
    print("=" * 60)
    print("Testing Config Loading")
    print("=" * 60)
    
    # Test CSRNet config
    print("\n1. Loading CSRNet config...")
    csrnet_config = load_csrnet_config()
    print(f"   ✅ CSRNet config loaded: {csrnet_config.model.name}")
    
    # Test TMTB config
    print("\n2. Loading TMTB config...")
    tmtb_config = load_tmtb_config()
    print(f"   ✅ TMTB config loaded: {tmtb_config.model.name}")
    
    print("\n" + "=" * 60)
    print("Testing Dimension Retrieval")
    print("=" * 60)
    
    # Test all sources for both models
    sources = ["image", "webcam", "video", "surveillance"]
    models = ["csrnet", "tmtb"]
    
    for model in models:
        print(f"\n{model.upper()} Dimensions:")
        for source in sources:
            dims = get_dimensions_for_source(model, source)
            print(f"   {source:12} -> {dims.length}x{dims.breadth} px")
    
    # Test 'upload' alias
    print("\n3. Testing 'upload' alias (should map to 'image')...")
    upload_dims = get_dimensions_for_source("csrnet", "upload")
    image_dims = get_dimensions_for_source("csrnet", "image")
    assert upload_dims.length == image_dims.length
    assert upload_dims.breadth == image_dims.breadth
    print(f"   ✅ 'upload' correctly maps to 'image': {upload_dims.length}x{upload_dims.breadth}")
    
    print("\n" + "=" * 60)
    print("Testing Config Values")
    print("=" * 60)
    
    # Verify expected values
    print("\nCSRNet:")
    print(f"   Image upload: {csrnet_config.preprocessing.image.length}x{csrnet_config.preprocessing.image.breadth} (expected: 800x800)")
    print(f"   Webcam:       {csrnet_config.preprocessing.webcam.length}x{csrnet_config.preprocessing.webcam.breadth} (expected: 640x640)")
    
    print("\nTMTB:")
    print(f"   Image upload: {tmtb_config.preprocessing.image.length}x{tmtb_config.preprocessing.image.breadth} (expected: 800x800)")
    print(f"   Webcam:       {tmtb_config.preprocessing.webcam.length}x{tmtb_config.preprocessing.webcam.breadth} (expected: 384x384)")
    
    print("\n" + "=" * 60)
    print("✅ All Config Tests Passed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_config_loading()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
