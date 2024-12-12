import json

from tome.api.output import TomeOutput
from tome.command import tome_command, CommandType
from tome.errors import TomeException


def print_serial(item, indent=None, color_index=None):
    indent = "" if indent is None else (indent + "  ")
    output = TomeOutput(stdout=True)
    if isinstance(item, dict):
        for k, v in item.items():
            if v is None:
                continue
            if isinstance(v, (str, int)):
                output.info(f"{indent}{k}: {v}")
            else:
                output.info(f"{indent}{k}")
                print_serial(v, indent, color_index)
    elif isinstance(item, type([])):
        for elem in item:
            output.info(f"{indent}{elem}")
    elif isinstance(item, int):  # Can print 0
        output.info(f"{indent}{item}")
    elif item:
        output.info(f"{indent}{item}")


def print_json_output(result):
    output = TomeOutput(stdout=True)
    output.print_json(json.dumps(result, indent=4))


@tome_command(formatters={"text": print_serial, "json": print_json_output})
def info(tome_api, parser, *args):
    """
    Get information about a command.
    """
    parser.add_argument("command_name", help="Name for the tome command.")
    args = parser.parse_args(*args)
    commands, _ = tome_api.list.filter_cli_commands(args.command_name, [CommandType.cache, CommandType.editable])
    try:
        command_info = commands[args.command_name]
        ret = command_info.serialize()
        return ret
    except KeyError:
        raise TomeException(f"Command '{args.command_name}' not found.")
