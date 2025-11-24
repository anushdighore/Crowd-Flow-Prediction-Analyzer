"""
Shared pytest fixtures for ML tests
"""
import pytest
from pathlib import Path
import sys
import torch
import cv2

# Add ml/src to path
ML_SRC = Path(__file__).parent / "src"
sys.path.insert(0, str(ML_SRC))


@pytest.fixture(scope="session")
def project_root():
    """Project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def ml_root():
    """ML directory root"""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def data_dir(project_root):
    """Data directory"""
    return project_root / "data"


@pytest.fixture(scope="session")
def test_images_dir(data_dir):
    """Test images directory"""
    return data_dir / "images"


@pytest.fixture(scope="session")
def test_videos_dir(data_dir):
    """Test videos directory"""
    return data_dir / "videos"


@pytest.fixture(scope="session")
def checkpoints_dir(ml_root):
    """Model checkpoints directory"""
    return ml_root / "checkpoints"


@pytest.fixture(scope="session")
def device():
    """Get compute device (cuda/cpu)"""
    return 'cuda' if torch.cuda.is_available() else 'cpu'


@pytest.fixture(scope="session")
def has_gpu():
    """Check if GPU is available"""
    return torch.cuda.is_available()


@pytest.fixture
def sample_crowd_image_high(test_images_dir):
    """Get a high-density crowd image"""
    crowd_dir = test_images_dir / "crowd" / "high_density"
    if crowd_dir.exists():
        images = list(crowd_dir.glob("*.jpg")) + list(crowd_dir.glob("*.png"))
        if images:
            return str(images[0])
    pytest.skip("No high-density test images found")


@pytest.fixture
def sample_crowd_image_medium(test_images_dir):
    """Get a medium-density crowd image"""
    crowd_dir = test_images_dir / "crowd" / "medium_density"
    if crowd_dir.exists():
        images = list(crowd_dir.glob("*.jpg")) + list(crowd_dir.glob("*.png"))
        if images:
            return str(images[0])
    pytest.skip("No medium-density test images found")


@pytest.fixture
def sample_crowd_image_low(test_images_dir):
    """Get a low-density crowd image"""
    crowd_dir = test_images_dir / "crowd" / "low_density"
    if crowd_dir.exists():
        images = list(crowd_dir.glob("*.jpg")) + list(crowd_dir.glob("*.png"))
        if images:
            return str(images[0])
    pytest.skip("No low-density test images found")


@pytest.fixture
def sample_video(test_videos_dir):
    """Get a sample test video"""
    video_dir = test_videos_dir / "test_samples"
    if video_dir.exists():
        videos = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.avi"))
        if videos:
            return str(videos[0])
    pytest.skip("No test videos found")


@pytest.fixture
def sample_video_crowd(test_videos_dir):
    """Get a crowd video"""
    video_dir = test_videos_dir / "crowd"
    if video_dir.exists():
        videos = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.avi"))
        if videos:
            return str(videos[0])
    pytest.skip("No crowd videos found")


@pytest.fixture
def create_dummy_image():
    """Factory for creating dummy test images"""
    def _create(width=640, height=480, channels=3):
        import numpy as np
        return np.random.randint(0, 255, (height, width, channels), dtype=np.uint8)
    return _create


@pytest.fixture
def create_dummy_video(tmp_path):
    """Factory for creating dummy test videos"""
    def _create(frames=30, width=640, height=480, fps=30):
        import numpy as np
        
        video_path = tmp_path / "test_video.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))
        
        for _ in range(frames):
            frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            out.write(frame)
        
        out.release()
        return str(video_path)
    
    return _create


@pytest.fixture(scope="session")
def csrnet_checkpoint(checkpoints_dir):
    """CSRNet checkpoint path"""
    checkpoint = checkpoints_dir / "csrnet.pth"
    if checkpoint.exists():
        return str(checkpoint)
    pytest.skip("CSRNet checkpoint not found")


@pytest.fixture(scope="session")
def mcnn_checkpoint(checkpoints_dir):
    """MCNN checkpoint path"""
    checkpoint = checkpoints_dir / "mcnn.pth"
    if checkpoint.exists():
        return str(checkpoint)
    pytest.skip("MCNN checkpoint not found")


# Marker for slow tests
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "gpu: marks tests that require GPU")
    config.addinivalue_line("markers", "integration: marks integration tests")


# Skip GPU tests if no GPU available
def pytest_collection_modifyitems(config, items):
    skip_gpu = pytest.mark.skip(reason="GPU not available")
    for item in items:
        if "gpu" in item.keywords and not torch.cuda.is_available():
            item.add_marker(skip_gpu)
