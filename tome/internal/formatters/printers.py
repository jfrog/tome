from tome.api.output import TomeOutput
from tome.command import CommandType
from tome.internal.cli.emojinator import Emojinator
from rich.text import Text


def print_command_docstrings(commands, namespaces):
    """
    Common printer which shows the namespaces, commands and their docs.

    :param commands: <dict command_name: <Command object>>
    :param namespaces: <dict namespace_name: [command_name1, ...]>
    """

    def _extract_docstring(docstring):
        lines = docstring.strip().split('\n')
        for i, line in enumerate(lines):
            if not line.strip():
                return ' '.join(lines[:i]).strip()
        return docstring.strip()

    output = TomeOutput(stdout=True)

    max_name_length = max(len(name) for name in commands) if commands else 0
    padding_size = max_name_length + 6
    emojinator = Emojinator()

    for namespace_name, comm_names in sorted(namespaces.items()):
        namespace_string = (
            Text(f"\n{emojinator.get_emoji(namespace_name)} {namespace_name} commands", style="bold magenta")
            if namespace_name
            else Text("\n📖 tome commands:", style="bold magenta")
        )
        output.info(namespace_string)

        for name in sorted(comm_names):
            command = commands[name]
            summary = _extract_docstring(command.doc) if command.doc else "No description."
            display_name = f"{name} (e)" if command.type == CommandType.editable else name
            padded_name = " " + display_name.ljust(padding_size)
            if command.type == CommandType.editable:
                command_string = Text(f"{padded_name}", style="yellow")
                summary_string = Text(f"{summary}")
            elif command.type == CommandType.failed:
                command_string = Text(padded_name)
                summary_string = Text(f"{summary}", style="bold red")
            else:
                command_string = Text(padded_name)
                summary_string = Text(f"{summary}")

            output.info(command_string + summary_string)
