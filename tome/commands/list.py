import json
from collections import defaultdict

from tome.api.output import TomeOutput
from tome.command import tome_command, CommandType
from tome.internal.formatters.printers import print_grouped_commands


def print_list_json(result):
    output = TomeOutput(stdout=True)

    commands, namespaces = result.get("list")
    pattern = result.get("pattern")

    list_results = defaultdict(dict)
    for namespace_name, comm_names in sorted(namespaces.items()):
        for name in sorted(comm_names):
            command = commands[name]
            list_results[namespace_name].update(
                {
                    command.name: {
                        "doc": command.doc,
                        "type": command.type.name,
                        "error": command.error,
                    }
                }
            )

    myjson = json.dumps({"results": list_results, "pattern": pattern}, indent=4)
    output.print_json(myjson)


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

    return result
