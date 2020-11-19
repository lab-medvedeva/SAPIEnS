#!/usr/bin/env python
"""
# Author: Xiong Lei
# Created Time : Thu 18 Oct 2018 02:42:37 PM CST

# File Name: setup.py
# Description:

"""

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    print(requirements)

setup(name='scale-atac',
      version='1.0.2',
      description='Single-Cell ATAC-seq Analysis via Latent feature Extraciton',
      packages=find_packages(),

      author='Lei Xiong',
      author_email='jsxlei@gmail.com',
      url='https://github.com/jsxlei/SCALE',
      scripts=['SCALE.py'],
      install_requires=requirements,
      python_requires='>3.6.0',

      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.7',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX :: Linux',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
     ],
     )
