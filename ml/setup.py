from setuptools import setup, find_packages

setup(
    name="crowd_models",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'numpy',
        'torch',
        'torchvision',
        'opencv-python',
        'Pillow',
        'timm',
        'einops',
    ],
    python_requires='>=3.8',
)
