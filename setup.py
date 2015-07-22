from __future__ import print_function
from setuptools import setup
import codecs
import os


setup(
    name='s3site',
    description='A command line tool to manage static sites on Amazons S3 service',
    version='0.2',
    py_modules=['s3site'],
    include_package_data=True,
    install_requires=[
        'PyYAML>=3.11',
        'arrow>=0.6.0',
        'boto>=2.38.0',
        'click>=4.0',
        'mock>=1.0.1',
    ],
    entry_points='''
        [console_scripts]
        s3site=s3site:cli
    ''',
    author_email='me@bensentorpy.com',
    author='Ben Olsen',
    url="https://github.com/bensentropy/s3site",
    download_url='https://github.com/bensentropy/s3site/archive/master.zip',
)
