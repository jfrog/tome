import fnmatch
import re

from tome.command import CommandType
from tome.errors import TomeException


# FIXME: probably there should not be a ListApi, maybe move all the logic to the Cli class
class ListApi:
    def __init__(self, tome_api):
        self.tome_api = tome_api
        self.cli = None

    # TODO: it'd be great if we could highlight the matches
    def filter_cli_commands(self, pattern, include):
        """
        Filtering all the available commands, and even help documentation. By default, built-in commands
        are excluded.

        :param pattern: pattern (str-like) to perform a search through the command names, and even the docs.
        :param include: list of CommandType values to be included in the final list. If None, all the types
                        will be included.
        """
        from tome.cli import Cli

        if not isinstance(self.cli, Cli):
            raise TomeException(f"Expected 'Cli' type, got '{type(self.cli).__name__}'")

        included = include or list(CommandType)

        # Check for exact command match first
        if pattern in self.cli.commands and self.cli.commands[pattern].type in included:
            namespace, command = pattern.split(":")
            return {pattern: self.cli.commands[pattern]}, {namespace: [pattern]}

        # If no exact match, proceed with existing filtering logic
        regex = re.compile(fnmatch.translate(pattern), flags=re.IGNORECASE)  # optimizing the match
        filtered_commands = {}
        filtered_namespaces = {}

        for namespace, commands in sorted(self.cli.namespaces.items()):
            # First search in namespace name, if match all the commands are included
            if regex.search(namespace):
                matched_commands = commands
            else:
                # Second search in command names
                matched_commands = [name for name in commands if regex.search(name)]
                # Third search in command docstrings
                matched_commands += [
                    name
                    for name in commands
                    if self.cli.commands[name].doc and regex.search(self.cli.commands[name].doc)
                ]

            # Filter commands by their type
            filtered_commands_in_namespace = [
                name
                for name in matched_commands
                if self.cli.commands.get(name) and self.cli.commands.get(name).type in included
            ]

            if filtered_commands_in_namespace:
                filtered_namespaces[namespace] = filtered_commands_in_namespace
                for name in filtered_commands_in_namespace:
                    filtered_commands[name] = self.cli.commands[name]

        return filtered_commands, filtered_namespaces
