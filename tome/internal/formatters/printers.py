from rich.text import Text

from tome.api.output import TomeOutput
from tome.command import CommandType
from tome.internal.cli.emojinator import Emojinator


def _extract_docstring(docstring):
    if not docstring:
        return "No description."
    lines = docstring.strip().split('\n')
    for i, line in enumerate(lines):
        if not line.strip():
            return ' '.join(lines[:i]).strip()
    return ' '.join(lines).strip()


def print_grouped_commands(result):
    output = TomeOutput(stdout=True)

    all_commands = [
        command for namespaces in result.values() for commands in namespaces.values() for command in commands
    ]

    if not all_commands:
        return

    max_name_length = max(
        (len(f"{cmd.namespace}:{cmd.name}" if cmd.namespace else cmd.name) for cmd in all_commands), default=0
    )

    base_padding = max_name_length + 6

    sorted_origins = sorted(result.items(), key=lambda item: (item[0] is None, item[0]))

    for origin, namespaces_data in sorted_origins:
        if origin is None:
            ns_indent = ""
            cmd_indent = "  "
        else:
            ns_indent = "  "
            cmd_indent = "     "
            if isinstance(origin, str):
                output.info(Text(f"\n📖 {origin}", style="bold white"))

        current_padding_size = base_padding

        for namespace, commands in sorted(namespaces_data.items()):
            if namespace is None:
                namespace_string = f"\n{ns_indent}📖 tome commands:"
            else:
                namespace_string = f"\n{ns_indent}{Emojinator().get_emoji(namespace)} {namespace} commands"

            output.info(Text(namespace_string, style="bold magenta"))

            for command in sorted(commands, key=lambda c: c.name):
                summary = _extract_docstring(command.doc)

                if command.type == CommandType.built_in:
                    display_name = command.name
                else:
                    fullname = f"{command.namespace}:{command.name}" if command.namespace else command.name
                    display_name = f"{fullname} (e)" if command.type == CommandType.editable else fullname

                padded_name = cmd_indent + display_name.ljust(current_padding_size)

                if command.type == CommandType.editable:
                    command_string = Text(padded_name, style="yellow")
                    summary_string = Text(summary)
                elif command.type == CommandType.failed:
                    command_string = Text(padded_name)
                    summary_string = Text(summary, style="bold red")
                else:
                    command_string = Text(padded_name)
                    summary_string = Text(summary)

                output.info(command_string + summary_string)
