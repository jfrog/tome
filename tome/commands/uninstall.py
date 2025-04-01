import json

from tome.api.output import TomeOutput
from tome.command import tome_command
from tome.internal.source import Source


def text_uninstall_formatter(source):
    output = TomeOutput(stdout=True)
    output.info(f"Uninstalled source: {source.uri}")


def json_uninstall_formatter(source):
    output = TomeOutput(stdout=True)
    data = {
        "uri": source.uri,
        "type": str(source.type),
        "version": source.version,
        "commit": source.commit,
        "folder": source.folder,
    }
    output.print_json(json.dumps(data, indent=4))


@tome_command(formatters={"text": text_uninstall_formatter, "json": json_uninstall_formatter})
def uninstall(tome_api, parser, *args):
    """
    Uninstall scripts from various sources.
    """
    parser.add_argument(
        "source",
        nargs='?',
        help="Source: a git repository, folder, or zip file (local or http).",
    )
    args = parser.parse_args(*args)

    source = Source.parse(args.source)
    return tome_api.install.uninstall_from_source(source)
