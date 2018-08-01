# coding=utf-8
from __future__ import print_function, absolute_import
import click



@click.group()
def cli():
    """
    a data process tool for GrADS binary data.
    """
    pass


@cli.command('grads-convert', short_help="convert GrADS data.")
@click.argument("config-file", nargs=-1, required=True)
def grads_convert(config_file):
    """Convert GrADS binary data file according to a config file."""
    from porter.grads_tool.grads_convert import GradsConvert
    converter = GradsConvert()
    for config_file in config_file:
        converter.convert(config_file)


@cli.command("grads-copy", short_help="copy GrADS data.")
@click.option("--where", "-w",
              help="where cause, key=value1|value2,key=value,...")
@click.option("--output", "-o", help="output file")
@click.argument("ctl-file", required=True)
def grads_copy(where, output, ctl_file):
    from porter.grads_tool.grads_copy import GradsCopy
    tool = GradsCopy(where, output)
    tool.process(ctl_file)


@cli.command("grib-copy", short_help="copy GRIB2 data.")
@click.option("--where", "-w",
              help="where cause, key=value1|value2,key=value,...")
@click.option("--range", "-r", "grid_range",
              help="latitude and longitude range, left_lon/right_lon/top_lat/bottom_lat")
@click.option("--output", "-o", help="output file")
@click.argument("grib-file", required=True)
def grads_copy(where, grid_range, output, grib_file):
    """Copy GRIB2 data."""
    from porter.grib_tool.grib_copy import GribCopy
    tool = GribCopy(where=where, grid_range=grid_range, output=output)
    tool.process(grib_file)


if __name__ == "__main__":
    cli()
