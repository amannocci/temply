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
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def read_requires(*file_paths):
    requires = []
    if os.path.isfile(*file_paths):
        raw_requires = read(*file_paths)
        requires.append(raw_requires.splitlines())
    return requires


install_requires = read_requires('requirements.txt')

tests_require = read_requires('requirements-tests.txt')

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
    name='temply',
    version=find_version("temply", "__init__.py"),
    description='Render jinja2 templates on the command line with shell environment variables.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/amannocci/temply',
    project_urls={
        'Documentation': 'https://github.com/amannocci/temply',
        'Changelog': 'https://github.com/amannocci/temply/CHANGELOG.md',
        'Source': 'https://github.com/amannocci/temply',
        'Tracker': 'https://github.com/amannocci/temply/issues'
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
        'console_scripts': ['temply=temply.temply:main']
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6'
    ]
)
