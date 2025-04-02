import json
from collections import defaultdict

from tome.api.output import TomeOutput
from tome.command import tome_command, CommandType
from tome.internal.formatters.printers import print_command_docstrings


def print_list_text(result):
    commands, namespaces = result.get("list")
    if commands and namespaces:
        TomeOutput(stdout=True).info(f"Results for '{result.get('pattern')}' pattern:")
        print_command_docstrings(commands, namespaces)
    else:
        TomeOutput(stdout=True).error(f"No matches were found for {result.get('pattern')} pattern.")


def print_list_json(result):
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

    output = TomeOutput(stdout=True)
    myjson = json.dumps({"results": list_results, "pattern": pattern}, indent=4)
    output.print_json(myjson)


@tome_command(formatters={"text": print_list_text, "json": print_list_json})
def list(tome_api, parser, *args):
    """
    List all the commands that match a given pattern.
    """
    parser.add_argument("pattern", nargs="?", help="Commands name pattern. By default, it shows all the commands")
    args = parser.parse_args(*args)
    # Adding a "*" at the end of each pattern if not given
    pattern = f"*{args.pattern}*" if args.pattern and "*" not in args.pattern else args.pattern or '*'
    commands, namespaces = tome_api.list.filter_cli_commands(pattern, [CommandType.cache, CommandType.editable])
    return {"list": (commands, namespaces), "pattern": pattern}
