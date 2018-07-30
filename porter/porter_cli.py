# coding=utf-8
from __future__ import print_function, absolute_import
import click

from porter.grads_tool.grads_convert import GradsConvert
from porter.grads_tool.grads_copy import GradsCopy


@click.group()
def cli():
    """
    a data process tool for GrADS binary data.
    """
    pass


@cli.command('grads-convert', help="convert GrADS data.")
@click.argument("config-file", nargs=-1, required=True)
def grads_convert(config_file):
    """
DESCRIPTION
    Convert GrADS binary data file according to a config file.
    """
    converter = GradsConvert()
    for config_file in config_file:
        converter.convert(config_file)


@cli.command("grads-copy", help="copy GrADS data.")
@click.option("--where", "-w", help="where cause")
@click.option("--output", "-o", help="output file")
@click.argument("ctl-file", required=True)
def grads_copy(where, output, ctl_file):
    tool = GradsCopy(where, output)
    tool.process(ctl_file)


@cli.command("grib-copy", help="copy GrADS data.")
@click.option("--where", "-w", help="where cause")
@click.option("--range", "-r", "grid_range", help="latitude and longitude range, lat1/lat2/lon1/lon2")
@click.option("--output", "-o", help="output file")
@click.argument("grib-file", required=True)
def grads_copy(where, grid_range, output, grib_file):
    from porter.grib_tool.grib_copy import GribCopy
    tool = GribCopy(where=where, grid_range=grid_range, output=output)
    tool.process(grib_file)


if __name__ == "__main__":
    cli()
