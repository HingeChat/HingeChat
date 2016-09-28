#!/usr/bin/env python2.7

from setuptools import setup
from setuptools import find_packages

setup(
    name='HingeChat',
    version='1.0.0',
    author='Pythonic Engineering',
    author_email='admin@pythonengineering.gov',
    url='https://github.com/HingeChat/HingeChat',
    license='LGPL3',
    description='An encrypted group chat program using the Hinge API',
    packages=find_packages(),
    package_data={
        'hingechat': ['images/*.png', 'images/light/*.png', 'images/dark/*.png']
    },
    install_requires=[
        'M2Crypto'
        # PyQt4 is also required, but it doesn't play nicely with setup.py
    ],
)
