# coding=utf-8
"""
porter: a tool for GrADS data converting
"""
from __future__ import print_function, absolute_import
import click

from porter.grads_converter import GradsConverter


@click.group()
def cli():
    pass


@cli.command('grads-convert', help="convert GrADS data.")
@click.argument("config-file", nargs=-1, required=True)
def grads_convert(config_file):
    """
DESCRIPTION
    Convert GrADS binary data file according to a config file.
"""
    converter = GradsConverter()
    for config_file in config_file:
        converter.convert(config_file)


if __name__ == "__main__":
    cli()
