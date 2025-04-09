import json
from collections import defaultdict

from tome.api.output import TomeOutput
from tome.command import tome_command, CommandType
from tome.errors import TomeException
from tome.internal.formatters.printers import print_grouped_commands


def print_list_json(result):
    output = TomeOutput(stdout=True)

    results = {}

    for origin, namespaces in result.items():
        origin_dict = results.setdefault(origin, {})
        for namespace, command_info_list in namespaces.items():
            namespace_dict = origin_dict.setdefault(namespace, {})
            for command_info in command_info_list:
                namespace_dict[command_info.name] = {
                    "doc": command_info.doc,
                    "type": command_info.type.name,
                    "error": command_info.error,
                }

    output.print_json(json.dumps(results, indent=4, ensure_ascii=False))


@tome_command(formatters={"text": print_grouped_commands, "json": print_list_json})
def list(tome_api, parser, *args):
    """
    List all the commands that match a given pattern.
    """
    parser.add_argument("pattern", nargs="?", help="Commands name pattern. By default, it shows all the commands")
    args = parser.parse_args(*args)
    # Adding a "*" at the end of each pattern if not given
    pattern = f"*{args.pattern}*" if args.pattern and "*" not in args.pattern else args.pattern or '*'

    filtered_commands = tome_api.list.filter_commands(pattern, [CommandType.cache, CommandType.editable])
    result = tome_api.list.group_commands(filtered_commands)

    if not result:
        TomeOutput().info(f"No matches were found for '{pattern}' pattern.")

    return result
