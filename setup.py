import codecs
import os
import re
import sys

import pkg_resources
from setuptools import setup, find_packages


def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


install_requires = [
    'click==7.1.2',
    'jsonschema==3.2.0'
]

tests_require = [
    'pytest==5.4.1',
    'tox==3.14.6'
]

extras_require = {
    'tests': tests_require
}

try:
    if 'bdist_wheel' not in sys.argv:
        for key, value in extras_require.items():
            if key.startswith(':') and pkg_resources.evaluate_marker(key[1:]):
                install_requires.extend(value)
except Exception as e:
    print("Failed to compute platform dependencies: {}. ".format(e) +
          "All dependencies will be installed as a result.", file=sys.stderr)
    for key, value in extras_require.items():
        if key.startswith(':'):
            install_requires.extend(value)

setup(
    name='templaty',
    version=find_version("templaty", "__init__.py"),
    description='templaty provide a way to build and test container images.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/amannocci/templaty',
    project_urls={
        'Documentation': 'https://github.com/amannocci/templaty',
        'Changelog': 'https://github.com/amannocci/templaty/CHANGELOG.md',
        'Source': 'https://github.com/amannocci/templaty',
        'Tracker': 'https://github.com/amannocci/templaty/issues'
    },
    author="amannocci",
    author_email="adrien.mannocci@gmail.com",
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=tests_require,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['templaty=templaty.templaty:main']
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6'
    ]
)

