# coding=utf-8
from __future__ import print_function, absolute_import
import click

from porter.grads_tool import cli as grads_tool_cli
from porter.grib_tool import cli as grib_tool_cli


@click.group()
def cli():
    """
    A data process tool for NWPC data.
    """
    pass


cli.add_command(grads_tool_cli.grads_convert)
cli.add_command(grads_tool_cli.grads_copy)
cli.add_command(grib_tool_cli.grib_copy)
cli.add_command(grib_tool_cli.grib_to_png)


if __name__ == "__main__":
    cli()
