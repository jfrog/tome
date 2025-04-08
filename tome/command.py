import argparse
import os
import subprocess
import textwrap
from enum import Enum

from tome.api.output import TomeOutput
from tome.errors import TomeException


class CommandType(Enum):
    built_in = "built-in"
    cache = "cache"  # FIXME: storehouse? ...?
    editable = "editable"
    failed = "failed"

    def __str__(self):
        return self.value


class SmartFormatter(argparse.HelpFormatter):
    def _fill_text(self, text, _, indent):
        text = textwrap.dedent(text)
        return ''.join(indent + line for line in text.splitlines(True))


class BaseTomeCommand:
    def __init__(self, method, formatters=None):
        self._formatters = {"text": lambda x: None}
        self._method = method
        self._name = None
        self._type = None  # built-in, cache, editable, ...
        self._init_formatters(formatters)
        self._init_doc()

        self.parser = None
        self.namespace = None
        self.module_name = None

    def _init_formatters(self, formatters):
        if formatters:
            for kind, action in formatters.items():
                if callable(action):
                    self._formatters[kind] = action
                else:
                    raise TomeException(f"Invalid formatter for {kind}. The formatter must be a valid function")

    def _init_doc(self):
        if self._method.__doc__:
            self._doc = self._method.__doc__.strip()
        else:
            self._doc = "No description provided for this command."
            TomeOutput().warning(
                f"The command '{self._name}' is missing a docstring. Consider adding one with a description of the command."
            )

    @property
    def _available_formatters(self):
        """
        Formatters that are shown as available in help, 'text' formatter
        should not appear
        """
        return [formatter for formatter in self._formatters if formatter != "text"]

    @property
    def fullname(self):
        return f"{self.namespace}:{self.name}"

    @property
    def name(self):
        return self._name

    @property
    def method(self):
        return self._method

    @property
    def doc(self):
        return self._doc

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        assert isinstance(value, CommandType)
        self._type = value

    def _format_command_output(self, info, *args):
        parser_args, _ = self.parser.parse_known_args(*args)

        default_format = "text"
        try:
            formatarg = parser_args.format or default_format
        except AttributeError:
            formatarg = default_format

        try:
            formatter = self._formatters[formatarg]
        except KeyError as error:
            raise TomeException(
                f"{formatarg} is not a known format. Supported formatters are: {', '.join(self._available_formatters)}"
            ) from error

        formatter(info)


class TomeArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._subparser = None
        self._init_log_levels()

    def _init_log_levels(self):
        self.add_argument(
            '-v',
            '--verbose',
            action='count',
            default=0,
            help="Increase the level of verbosity (use -v, -vv, -vvv, etc.)",
        )
        self.add_argument(
            '-q', '--quiet', action='store_true', help="Reduce the output to a minimum, showing only critical errors"
        )

    def add_formatters_argument(self, commands_formatters):
        if commands_formatters:
            help_message = f"Select the output format: {', '.join(commands_formatters)}"
            self.add_argument('-f', '--format', help=help_message)

    @property
    def subparser(self):
        return self._subparser

    @subparser.setter
    def subparser(self, value):
        self._subparser = value

    def parse_args(self, args=None, namespace=None):
        parsed_args = super().parse_args(args)
        TomeOutput.define_log_level(parsed_args.verbose, parsed_args.quiet)
        return parsed_args


class TomeCommand(BaseTomeCommand):
    def __init__(self, method, parent=None, formatters=None):
        super().__init__(method, formatters=formatters)
        self._name = method.__name__.replace("_", "-")
        self.subcommands = {}
        self.base_folder = None
        self.parent = parent
        self._init_parser()

    def _init_parser(self):
        if self.parent is None:
            self.parser = TomeArgumentParser(
                description=self._doc,
                prog=f"tome {self._name}",
                formatter_class=SmartFormatter,
            )
        else:
            if not self.parent.parser.subparser:
                subparser = self.parent.parser.add_subparsers(
                    dest=f'{self.parent.name}_subcommand', help='sub-command help'
                )
                subparser.required = True
                self.parent.parser.subparser = subparser
            else:
                subparser = self.parent.parser.subparser

            self.parser = subparser.add_parser(self._name, help=self._doc)
            self.parent.subcommands[self.name] = self
        self.parser.add_formatters_argument(self._available_formatters)

    def run(self, tome_api, *args):
        info = self._method(tome_api, self.parser, *args)

        if not self.subcommands:
            self._format_command_output(info, *args)
        else:
            try:
                subcommand = self.subcommands[args[0][0]]
                args = args[0][1:]  # Remove the subcommand from the args
            except (KeyError, IndexError):  # display help
                self.parser.parse_args(*args)
            else:
                subcommand.run(tome_api, args)  # Call run on the subcommand


class TomeShellCommand(BaseTomeCommand):
    def __init__(self, script):
        runner, description = self._get_runner_description(script)

        def method_wrapper(tome_api, parser, *args, **kwargs):  # noqa
            command = [*runner, script, *[str(arg) for arg in args]]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.stdout:
                TomeOutput(stdout=True).print(result.stdout.strip())
            if result.stderr:
                TomeOutput().print(result.stderr.strip())

        method_wrapper.__name__ = os.path.splitext(os.path.basename(script))[0].replace("-", "_")
        method_wrapper.__doc__ = description
        super().__init__(method=method_wrapper)

        basename = os.path.basename(script)[len("tome_") :]
        self._name = basename.replace("_", "-").replace(".", "-")
        self.parser = TomeArgumentParser(
            description=self._doc, prog=f"tome {self._name}", formatter_class=SmartFormatter
        )

    def run(self, tome_api, *args):
        if any(arg in ('--help', '-h') for arg in args[0]):
            TomeOutput().info(self._doc)
        else:
            self._method(tome_api, self.parser, *args[0])

    @staticmethod
    def _get_runner_description(script):
        runner, description = None, None
        with open(script, 'r') as f:
            for line in f:
                line = line.strip()
                if runner is None:
                    runner = line.replace('#!', '').split() if line.startswith('#!') else False
                if 'tome_description:' in line:
                    description = line.split('tome_description:', 1)[1].strip()
                    break

        # If not, try with extension
        if not runner:
            ext = os.path.splitext(script)[1]
            runner = {
                '.bat': [],
                '.ps1': ['powershell.exe', '-noexit', '-File'],
                '.sh': ['/bin/sh'],
                '.bash': ['/bin/bash'],
                '.zsh': ['/bin/zsh'],
            }.get(ext)
            if runner is None:
                raise TomeException(
                    f"Could not deduce the interpreter for script '{script}'. Try adding a shebang line (e.g., '#!/bin/sh') "
                    "or using a supported file extension like '.sh', '.bash', '.zsh', '.bat', or '.ps1'."
                )

        description = description or f"Command to run the script: {' '.join(runner)} {script}"
        return runner, description


def tome_command(parent=None, formatters=None):
    return lambda f: TomeCommand(f, parent=parent, formatters=formatters)
