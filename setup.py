from setuptools import setup, find_packages

setup(
    name="crowd_flow_analyzer",
    version="0.1.0",
    packages=find_packages(include=["models", "models.*", "utils", "utils.*"]),
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "opencv-python",
        "numpy",
        "torch",
    ],
    python_requires=">=3.9",
)
