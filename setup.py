from setuptools import setup, find_packages

setup(
    name="sharepycrud",
    version="0.1.0",
    author="Willem Seethaler",
    author_email="wcs@bu.edu",
    description="Python library for CRUD operations on SharePoint",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.32.3",
        "python-dotenv>=1.0.1",
    ],
    extras_require={
        "dev": [
            "black>=24.8.0",
            "mypy>=1.11.2",
            "pytest>=8.3.2",
            "types-setuptools==75.6.0.20241223",
        ],
        "test": [
            "pytest>=8.3.2",
            "pytest-mock>=3.14.0",
        ],
        "all": [
            "black>=24.8.0",
            "mypy>=1.11.2",
            "pytest>=8.3.2",
            "pytest-mock>=3.14.0",
            "types-setuptools==75.6.0.20241223",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.12.3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
    ],
)
