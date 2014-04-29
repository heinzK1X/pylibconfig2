#!/usr/bin/env python

from setuptools import setup

setup(
    name='pylibconfig2',
    description="Pure python library for libconfig syntax.",
    version='0.1.2',
    author="Heiner Tholen",
    author_email="github@heinertholen.com",
    url="https://github.com/heinzK1X/pylibconfig2",
    keywords="libconfig libconfig++ pylibconfig2 pylibconfig config",
    packages=['pylibconfig2', ],
    license='GPLv3',
    long_description=open('README.rst').read(),
    test_suite="pylibconfig2.test.test.suite",
)

