import json

from tome.api.output import TomeOutput
from tome.command import tome_command


def print_config_text(result):
    TomeOutput(stdout=True).print(result)


@tome_command()
def config(tome_api, parser, *args):  # noqa
    """
    Manage the tome configuration.
    """


@tome_command(parent=config, formatters={"text": print_config_text})
def home(tome_api, parser, *args):  # noqa
    """print the current home folder"""
    parser.parse_args(*args)
    return tome_api.cache_folder


@tome_command(parent=config, formatters={"text": print_config_text})
def store(tome_api, parser, *args):  # noqa
    """print the current store folder"""
    parser.parse_args(*args)
    return tome_api.store.folder
