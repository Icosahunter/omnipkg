import sys
import os
from setuptools import setup, find_packages

setup(
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True
)