# coding: utf-8

import click


@click.command("grib-copy", short_help="copy GRIB2 data.")
@click.option("--where", "-w",
              help="where cause, key=value1|value2,key=value,...")
@click.option("--range", "-r", "grid_range",
              help="latitude and longitude range, left_lon/right_lon/top_lat/bottom_lat")
@click.option("--output", "-o", help="output file")
@click.argument("grib-file", required=True)
def grib_copy(where, grid_range, output, grib_file):
    """Copy GRIB2 data."""
    from porter.grib_tool.grib_copy import GribCopy
    tool = GribCopy(where=where, grid_range=grid_range, output=output)
    tool.process(grib_file)


@click.command("grib-to-image", short_help="convert GRIB2 to image.")
@click.option("--where", "-w",
              help="where cause, key=value1|value2,key=value,...")
@click.option("--range", "-r", "grid_range",
              help="latitude and longitude range, left_lon/right_lon/top_lat/bottom_lat")
@click.option("--output", "-o", help="output file")
@click.option("--image-type", "-t", help="output image type", type=click.Choice(['png', 'jpeg']), default="png")
@click.argument("grib-file", required=True)
def grib_to_png(where, grid_range, output, image_type, grib_file):
    """Convert GRIB2 fields to PNG."""
    from porter.grib_tool.grib_to_image import GribToImageConverter
    tool = GribToImageConverter(where=where, grid_range=grid_range, output=output, image_type=image_type)
    tool.process(grib_file)
