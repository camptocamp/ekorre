#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import ekorre

setup(
    name='ekorre',

    version='0.1.0',
    packages=find_packages(),
    author="Léo Depriester",
    author_email="leo.depriester@camptocamp.com",
    entry_points = {
        'console_scripts': [
            'ekorre = ekorre.core:main',
        ],
    },
    license="Apache 2",
)
