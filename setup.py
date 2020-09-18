#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='j1708',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['j1708dump=j1708:main'],
    },
    install_requires=required,
)
