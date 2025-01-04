from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sharepycrud",
    version="0.1.2",
    author="Willem Seethaler",
    author_email="wcs@bu.edu",
    description="Python library for CRUD operations on SharePoint",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "dataclasses-json==0.6.7",
        "requests==2.32.3",
        "python-dotenv==1.0.1",
    ],
    extras_require={
        "dev": [
            "black>=24.8.0",
            "mypy==1.11.2",
            "pydantic==2.8.2",
            "types-requests==2.31.0",
            "types-setuptools==75.6.0.20241223",
            "pre-commit==4.0.1",
        ],
        "test": [
            "pytest==8.3.2",
            "pytest-mock==3.14.0",
        ],
        "all": [
            "black>=24.8.0",
            "mypy==1.11.2",
            "pydantic==2.8.2",
            "pytest==8.3.2",
            "pytest-mock==3.14.0",
            "types-requests==2.31.0",
            "types-setuptools==75.6.0.20241223",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.12.3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
