#!/usr/bin/env python

from setuptools import setup, find_packages
import asn1tools

setup(name='asn1tools',
      version=asn1tools.__version__,
      description='ASN.1 parsing, encoding and decoding.',
      long_description=open('README.rst', 'r').read(),
      author='Erik Moqvist',
      author_email='erik.moqvist@gmail.com',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
      keywords=['ASN.1', 'asn1'],
      url='https://github.com/eerimoq/asn1tools',
      packages=find_packages(exclude=['tests']),
      install_requires=['pyparsing>=2.2.0'],
      test_suite="tests",
      entry_points = {
          'console_scripts': ['asn1tools=asn1tools.__init__:_main']
      })
