from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='porter',

    version='0.1.0',

    description='',
    long_description=long_description,

    url='https://github.com/perillaroc/porter',

    author='perillaroc',
    author_email='perillaroc@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
        'Programming Language :: Python :: 3.6'
    ],

    keywords='',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=[
        'click',
        'pathlib2;python_version<"3.5"'
    ],

    extras_require={
        'tests': ['pytest'],
    },

    entry_points={}
)