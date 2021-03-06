#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='configcontextualchecker',
    author='Antoine Dechaume',
    version=open('VERSION').read().strip(),
    url='https://github.com/AntoineD/configcontextualchecker',
    download_url='https://pypi.python.org/pypi/configcontextualchecker',
    packages=['configcontextualchecker'],
    install_requires=['networkx', 'ply'],
    description='Contextual checking and default settings for config files',
    long_description=open('README.rst').read(),
    keywords='config contextual checker configobj',
    platforms=['POSIX'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities',
    ],
)
