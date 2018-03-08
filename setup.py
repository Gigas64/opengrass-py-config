"""

A setuptools based setup module
with single-source versioning

See:
https://packaging.python.org/en/latest/distributing.html
https://packaging.python.org/guides/single-sourcing-package-version/

"""
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
import re

here = path.abspath(path.dirname(__file__))

def read(*parts):
    filename = path.join(here, *parts)
    with open(filename, encoding='utf-8') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='opengrass_config-py-config',
    version=find_version('opengrass_config', '__init__.py'),
    description='opengrass_config-py-config provides a set of utility to ease the '
                'transition of DS Discovery activities into productization',
    long_description=read('README.rst'),
    url='http://github.com/gigas64/opengrass_config-py-config',
    author='Gigas64',
    author_email='gigas64@opengrass_config.net',
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='Configuration Singleton Thread-Safe Config',
    packages=find_packages(exclude=['tests', 'guides', 'data']),
    license='BSD',
    include_package_data=True,
    package_data={
        # If any package contains *.yaml files, include them:
        '': ['*.yaml'],
    },
    test_suite='tests',
)
