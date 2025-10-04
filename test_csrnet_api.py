"""
Test script to send an image to CSRNet API and display count in CLI
"""
import requests
from PIL import Image
import numpy as np
import io

def create_test_image():
    """Create a simple test image"""
    # Create a 512x512 RGB image with some noise
    img_array = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    return img

def test_csrnet_api():
    """Send test image to CSRNet API and display results"""
    
    print("\n" + "="*60)
    print("🧪 TESTING CSRNET API")
    print("="*60 + "\n")
    
    # API endpoint
    url = "http://localhost:8000/count"
    
    # Create test image
    print("📸 Creating test image...")
    test_img = create_test_image()
    
    # Convert image to bytes
    img_bytes = io.BytesIO()
    test_img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Send to API
    print("📤 Sending image to API...")
    files = {'file': ('test_image.png', img_bytes, 'image/png')}
    
    try:
        response = requests.post(url, files=files)
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        print("\n✅ SUCCESS! API Response:")
        print(f"   Filename: {result['filename']}")
        print(f"   Image Size: {result['image_size']}")
        print(f"   Density Map Shape: {result['density_map_shape']}")
        print(f"\n" + "="*60)
        print(f"   🎯 CROWD COUNT: {result['count']} people")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print("💡 Make sure the API server is running:")
        print("   cd models/csrnet")
        print("   python api.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        if hasattr(e, 'response'):
            print(f"   Response: {e.response.text}")

if __name__ == "__main__":
    test_csrnet_api()
