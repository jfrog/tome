import json

from tome.api.output import TomeOutput
from tome.command import CommandType, tome_command
from tome.errors import TomeException
from tome.internal.source import Source


def print_uninstall_text(source):
    output = TomeOutput(stdout=True)
    output.info(f"Uninstalled source: {source.uri}")


def print_uninstall_json(source):
    output = TomeOutput(stdout=True)
    data = {
        "uri": source.uri,
        "type": str(source.type),
        "version": source.version,
        "commit": source.commit,
        "folder": source.folder,
    }
    output.print_json(json.dumps(data, indent=4))


@tome_command(formatters={"text": print_uninstall_text, "json": print_uninstall_json})
def uninstall(tome_api, parser, *args):
    """
    Uninstall a tome of scripts.
    """
    parser.add_argument(
        "source",
        nargs='?',
        help="Source: a git repository, folder, or zip file (local or http).",
    )
    args = parser.parse_args(*args)

    try:
        source = Source.parse(args.source)
        return tome_api.install.uninstall_from_source(source)
    except TomeException as e:
        if args.source and ":" in args.source:
            matching_commands = tome_api.list.filter_commands(args.source, [CommandType.cache, CommandType.editable])
            if len(matching_commands) == 1:
                origin = (
                    matching_commands[0].source.uri if matching_commands[0].source else matching_commands[0].base_folder
                )
                raise TomeException(
                    f"You are trying to uninstall a command '{args.source}' that is installed from the '{origin}' tome.\n"
                    f"To uninstall this command, you must uninstall the whole tome.\n"
                    f"Please try running: \"tome uninstall '{origin}'\" if you want to uninstall the whole set of scripts from that tome.\n"
                ) from e
        else:
            raise e
