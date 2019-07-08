from __future__ import print_function
from setuptools import setup
import codecs
import os


setup(
    name='s3site',
    description='A command line tool to manage static sites on Amazons S3 service',
    version='0.2.1',
    py_modules=['s3site'],
    include_package_data=True,
    install_requires=[
        'PyYAML>=5.1.1',
        'arrow>=0.14.2',
        'boto3>=',
        'click>=7.0',
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
