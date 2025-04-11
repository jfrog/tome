import json

from tome.api.output import TomeOutput
from tome.command import tome_command, CommandType
from tome.errors import TomeException


def print_info_text(item, indent=None, color_index=None):
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
                print_info_text(v, indent, color_index)
    elif isinstance(item, type([])):
        for elem in item:
            output.info(f"{indent}{elem}")
    elif isinstance(item, int):  # Can print 0
        output.info(f"{indent}{item}")
    elif item:
        output.info(f"{indent}{item}")


def print_info_json(result):
    output = TomeOutput(stdout=True)
    output.print_json(json.dumps(result, indent=4))


@tome_command(formatters={"text": print_info_text, "json": print_info_json})
def info(tome_api, parser, *args):
    """
    Get information about a specific command.
    """
    parser.add_argument("command_name", help="The full name of the command (e.g., namespace:command).")
    args = parser.parse_args(*args)

    filtered_list = tome_api.list.filter_commands(args.command_name, [CommandType.cache, CommandType.editable])

    if len(filtered_list) == 1:
        found_command = filtered_list[0]
        return found_command.serialize()
    else:
        raise TomeException(f"Command '{args.command_name}' not found.")
