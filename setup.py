#!/usr/bin/env python3

from setuptools import setup, find_packages

__version__ = 

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='j1708',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'j1708dump=j1708:main',
            'parse485log=j1708:parse485log',
        ],
    },
    install_requires=required,
    version='0.0.1',
    python_requires='>=3.8',
)
