# coding: utf-8
import click


@click.command('grads-convert', short_help="convert GrADS data.")
@click.argument("config-file", nargs=-1, required=True)
def grads_convert(config_file):
    """Convert GrADS binary data file according to a config file."""
    from porter.grads_tool.grads_convert import GradsConvert
    converter = GradsConvert()
    for config_file in config_file:
        converter.convert(config_file)


@click.command("grads-copy", short_help="copy GrADS data.")
@click.option("--where", "-w",
              help="where cause, key=value1|value2,key=value,...")
@click.option("--output", "-o", help="output file")
@click.argument("ctl-file", required=True)
def grads_copy(where, output, ctl_file):
    """Copy GRADS data. Only binary data is copied. User must write ctl file."""
    from porter.grads_tool.grads_copy import GradsCopy
    tool = GradsCopy(where, output)
    tool.process(ctl_file)
