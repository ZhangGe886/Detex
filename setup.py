# -*- coding: utf-8 -*-
"""
Created on Mon Feb 29 19:49:03 2016

@author: derrick
"""
from setuptools import setup, find_packages
import os

version_file = os.path.join('detex', 'version.py')
with open(version_file) as vfopen:
    __version__ = vfopen.read().strip()

setup(
    name='detex',
    version = __version__,
    description = 'A package for performing subspace and correlation detections on seismic data',
    url = 'https://github.com/d-chambers/detex',
    author = 'Derrick Chambers',
    author_email = 'djachambeador@gmail.com',
    license = 'MIT',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Geo-scientists',
        'Topic :: Earthquake detection',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords = 'seismology signal detection',
    packages = find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires = ['obspy', 'basemap', 'numpy', 'pandas >= 0.17.0', 
                        'scipy', 'matplotlib', 'multiprocessing', 'glob2'],
)
