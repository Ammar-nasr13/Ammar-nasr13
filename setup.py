"""
from setuptools import setup, find_packages

setup(
    name="github-profile-generator",
    version="2.0.0",
    description="Professional GitHub Profile Statistics Generator",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "numpy>=1.24.0",
        "python-dateutil>=2.8.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "github-profile-gen=github_profile_generator:main",
        ],
    },
)
"""
