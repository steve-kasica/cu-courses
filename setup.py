"""
    setup.py

    Setup script for the CLI.

"""

from setuptools import setup
from src.__main__ import SCRIPT_DESCRIPTION

setup(
    name="cu-courses",
    version="1.0.0",
    description='A scraper for the University of Colorado Boulder Course Catalog',
    long_description=SCRIPT_DESCRIPTION,
    author="Stephen Kasica",
    author_email="stephen.kasica@colorado.edu",
    maintainer="Stephen Kasica",
    maintainer_email="stephen.kasica@colorado.edu",
    url="https://github.com/stvkas/cu-courses",
    entry_points={
        "console_scripts": [
            'cu-courses = src.__main__:main',
        ]
    },
    packages=['src'],
    install_requires=[
        'beautifulsoup4',
        'requests'
    ]
)
