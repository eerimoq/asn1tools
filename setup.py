#!/usr/bin/env python

from setuptools import setup, find_packages
import asn1tools

setup(name='asn1tools',
      version=asn1tools.__version__,
      description='ASN.1 tools.',
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
      test_suite="tests")
