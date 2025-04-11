import fnmatch
import re
from collections import defaultdict

from tome.command import CommandType
from tome.errors import TomeException


# FIXME: probably there should not be a ListApi, maybe move all the logic to the Cli class
class ListApi:
    def __init__(self, tome_api):
        self.tome_api = tome_api
        self.cli = None

    def filter_commands(self, pattern, types=None):
        """
        Filter commands based on a search pattern and allowed command types.

        :param pattern: The search pattern to filter command names and documentation.
        :param types: List CommandType values. If not provided, all command types are considered.
        :return: A list of CommandInfo objects that match the search pattern.
        """
        from tome.cli import Cli

        if not isinstance(self.cli, Cli):
            raise TomeException(f"Expected 'Cli' type, got '{type(self.cli).__name__}'")

        included_types = types or list(CommandType)
        result = []

        commands = {
            name: command_info
            for name, command_info in self.cli.commands.items()
            if command_info.type in included_types
        }

        # Exact match: if the pattern exactly matches a command's full name, return it immediately.
        if pattern in commands:
            return [commands[pattern]]

        regex = re.compile(fnmatch.translate(pattern), flags=re.IGNORECASE)

        for command_name, command_info in commands.items():
            if regex.search(command_name):
                result.append(command_info)
            elif command_info.doc and regex.search(command_info.doc):
                result.append(command_info)

        return result

    def group_commands(self, commands_list):
        grouped_data = defaultdict(lambda: defaultdict(list))

        if not commands_list:
            return {}

        for command_info in commands_list:
            if command_info.type == CommandType.built_in:
                source_uri = None
            else:
                source_uri = command_info.source.uri if command_info.source else command_info.base_folder

            grouped_data[source_uri][command_info.namespace].append(command_info)

        return grouped_data
