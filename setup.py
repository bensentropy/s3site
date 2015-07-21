from __future__ import print_function
from setuptools import setup
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()

long_description = read('README.md')


setup(
    name='s3site',
    description='A command line tool to manage static sites on Amazons S3 service',
    long_description=long_description,
    version='0.1',
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
)
