#!/usr/bin/env python3

from setuptools import setup, find_packages

__version__ = '0.2'

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='j1708',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'j1708dump=j1708.cli.dump:main',
            'j1708sniff=j1708.cli.sniff:main',
        ],
    },
    install_requires=required,
    version=__version__ ,
    python_requires='>=3.8',
)
