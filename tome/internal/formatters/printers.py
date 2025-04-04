from tome.api.output import TomeOutput
from tome.command import CommandType
from tome.internal.cli.emojinator import Emojinator
from rich.text import Text


def print_grouped_commands(result):
    def _extract_docstring(docstring):
        lines = docstring.strip().split('\n')
        for i, line in enumerate(lines):
            if not line.strip():
                return ' '.join(lines[:i]).strip()
        return docstring.strip()

    output = TomeOutput(stdout=True)

    max_name_length = max(
        (
            len(f"{command.namespace}:{command.name}")
            for namespace in result.values()
            for commands in namespace.values()
            for command in commands
        ),
        default=0,
    )

    padding_size = max_name_length + 6

    for origin, namespace in result.items():
        if origin is not None:
            output.info(Text(f"\n\n📖 {origin}", style="bold white"))

        for namespace, commands in namespace.items():
            namespace_string = (
                Text(f"\n {Emojinator().get_emoji(namespace)} {namespace} commands", style="bold magenta")
                if namespace is not None
                else Text("\n📖 tome commands:", style="bold magenta")
            )

            output.info(namespace_string)

            for command in commands:
                summary = _extract_docstring(command.doc) if command.doc else "No description."
                if command.type == CommandType.editable:
                    display_name = f"{command.namespace}:{command.name} (e)"
                elif command.type == CommandType.built_in:
                    display_name = f"{command.name}"
                else:
                    display_name = f"{command.namespace}:{command.name}"

                padded_name = "    " + display_name.ljust(padding_size)
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
