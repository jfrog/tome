import os
import sys
import json
from tome.api.output import TomeOutput
from tome.command import tome_command
from tome.errors import TomeException
from tome.internal.source import Source, SourceType


def text_install_formatter(data):
    output = TomeOutput(stdout=True)
    output.info(f"Installed source: {data.get('installed')}")
    output.info(f"Message: {data.get('message')}")


def json_install_formatter(data):
    output = TomeOutput(stdout=True)
    output.print_json(json.dumps(data, indent=4))


@tome_command(formatters={"text": text_install_formatter, "json": json_install_formatter})
def install(tome_api, parser, *args):
    """
    Install scripts from a source.

    The source can be a git repository, a folder, or a zip file (local or http).
    Editable installations are supported with the -e/--editable flag.
    """
    parser.add_argument(
        "source",
        nargs="?",
        help="Source: a git repository, folder, or zip file (local or http).",
    )
    parser.add_argument("-e", "--editable", action="store_true", help="Install a package in editable mode.")
    parser.add_argument("--no-ssl", action="store_true", help="Do not verify SSL connections.")
    parser.add_argument(
        "--create-env",
        action="store_true",
        help="Create a new virtual environment if the command depends on any requirements.",
    )
    parser.add_argument(
        "--force-requirements",
        action="store_true",
        help="Force installation of requirements even if not running in a virtual environment.",
    )
    parser.add_argument(
        "--folder", help="Specify a folder within the source to install from (only valid for git or zip file sources)."
    )
    args = parser.parse_args(*args)

    # check using source similar to: https://pip.pypa.io/en/latest/topics/vcs-support/
    source = Source.parse(args.source)
    # Allow --folder only for sources of type GIT or FILE.
    # this does not make sense for local folders because you can already specify the folder in the source
    if args.folder:
        if source.type not in (SourceType.GIT, SourceType.FILE, SourceType.URL):
            raise TomeException("--folder argument is only compatible with git repositories and file sources.")
        source.folder = args.folder

    source.verify_ssl = not args.no_ssl

    try:
        if args.editable:
            source.type = SourceType.EDITABLE
            tome_api.install.install_editable(source, args.force_requirements, args.create_env)
            result = {"installed": source.uri, "message": "Editable installation succeeded."}
        else:
            tome_api.install.install_from_source(source, args.force_requirements, args.create_env)
            result = {"installed": source.uri, "message": "Installation succeeded."}
    except TomeException as e:
        TomeOutput().warning(f"Failed to install {source.uri}: {str(e)}")
        raise

    return result
