from setuptools import setup, find_packages
import codecs
from os import path

here = path.abspath(path.dirname(__file__))

with codecs.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='porter',

    version='0.2.0',

    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/perillaroc/porter',

    author='perillaroc',
    author_email='perillaroc@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ],

    keywords='',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=[
        'click',
        'pyyaml',
        'numpy',
        'scipy',
        'pathlib2;python_version<"3.5"'
    ],

    extras_require={
        'tests': ['pytest'],
    },

    entry_points={
        'console_scripts': [
            'porter = porter.porter_cli:cli'
        ]
    }
)