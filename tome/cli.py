import ast
import importlib
import importlib.util
import json
import os
import pkgutil
import signal
import sys
import traceback
from difflib import get_close_matches
from tome.api.api import TomeAPI
from tome.api.output import TomeOutput
from tome.command import CommandType, TomeCommand, TomeShellCommand
from tome.errors import TomeException, exception_message_safe
from tome.exit_codes import ERROR_GENERAL, ERROR_SIGTERM, ERROR_UNEXPECTED, SUCCESS, USER_CTRL_BREAK, USER_CTRL_C
from tome.internal.cache import TomePaths
from tome.internal.formatters.printers import print_grouped_commands
from tome.internal.source import Source
from tome.internal.utils.files import load


class CommandInfo:
    def __init__(
        self,
        namespace,
        name,
        command_doc,
        command_type,
        module_name,
        base_folder,
        command=None,
        error=None,
        env_path=None,
        source=None,
    ):
        self.command = command
        self.namespace = namespace
        self.doc = command_doc
        self.type = command_type
        self.name = name
        self.module_name = module_name
        self.base_folder = base_folder
        self.error = error
        self.env_path = env_path
        self.source = source

    def serialize(self):
        return {
            "namespace": self.namespace,
            "name": self.name,
            "doc": self.doc,
            "type": str(self.type),
            "module_name": self.module_name,
            "base_folder": self.base_folder,
            "error": self.error,
            "env_path": self.env_path,
            "source": self.source.serialize() if self.source else None,
        }


class Cli:
    """
    A single command of the tome application, with all the first level commands. Manages the
    parsing of parameters and delegates functionality to the tome python api. It can also show the
    help of the tool.
    """

    def __init__(self, tome_api):
        if not isinstance(tome_api, TomeAPI):
            raise TomeException(f"Expected 'TomeAPI' type, got '{type(tome_api).__name__}'")
        self._tome_api = tome_api
        self._tome_api.list.cli = self
        self._commands = {}
        # Temporary fix: loading editable file just once, not all the time
        self._editables = []
        editables_file = TomePaths(self._tome_api.cache_folder).editables_path
        if os.path.isfile(editables_file):
            with open(editables_file) as f:
                self._editables = json.load(f)

    @property
    def namespaces(self):
        _namespaces = {}
        for k, v in self._commands.items():
            _namespaces.setdefault(v.namespace, []).append(k)
        return _namespaces

    @property
    def commands(self):
        return self._commands

    def _add_builtin_commands(self):
        """Load tome own commands."""
        tome_built_in_commands_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "commands")
        for module in pkgutil.iter_modules([tome_built_in_commands_path]):
            module_name = module.name
            self._add_tome_commands_in_module(
                tome_built_in_commands_path, f"tome.commands.{module_name}", command_type=CommandType.built_in
            )

    def _load_commands_from_path(self, scripts_path, command_type=None, source=None):
        """Load commands from a directory"""
        old_sys_path = sys.path[:]
        try:
            sys.path.append(scripts_path)
            for namespace in os.listdir(scripts_path):
                namespace_folder_path = os.path.join(scripts_path, namespace)
                if not os.path.isdir(namespace_folder_path):
                    continue
                sys.path.append(namespace_folder_path)

                for module_info in pkgutil.iter_modules([namespace_folder_path]):
                    module_name = module_info.name
                    try:
                        # FIXME: we need to do some refactors around all these to avoid passing
                        #  so much repeated information
                        self._add_tome_commands_in_module(
                            namespace_folder_path,
                            module_name,
                            package=namespace,
                            base_folder=scripts_path,
                            command_type=command_type,
                            source=source,
                        )
                    except Exception as e:
                        TomeOutput().error(f"Error loading command '{module_name}.py' from '{scripts_path}': {e}")

                for _script in os.listdir(namespace_folder_path):
                    if _script.startswith("tome_"):
                        script = os.path.join(namespace_folder_path, _script)
                        item = TomeShellCommand(script)
                        self._register_command(
                            item, namespace, base_folder=scripts_path, command_type=command_type, source=source
                        )
        finally:
            sys.path = old_sys_path

    def _add_editable_commands(self):
        """Load command modules from editable installations."""
        for editable in self._editables:
            self._load_commands_from_path(editable["source"], command_type=CommandType.editable)

    def _add_cache_commands(self):
        """Load tome scripts installed in the cache."""

        tome_scripts_path = TomePaths(self._tome_api.cache_folder).scripts_path

        # FIXME: should we error out if commands overlap? should we allow multiple commands with the same name?
        # we need to sort the origins by modification time, so the most recent ones are loaded first
        # then, when two commands collide because they have the same name the first one that
        # was installed is the one that is kept

        origins = [
            origin for origin in os.listdir(tome_scripts_path) if os.path.isdir(os.path.join(tome_scripts_path, origin))
        ]

        origins.sort(key=lambda origin: os.path.getmtime(os.path.join(tome_scripts_path, origin)), reverse=True)

        for origin in origins:
            origin_folder = os.path.join(tome_scripts_path, origin)
            if not os.path.isdir(origin_folder):
                continue
            # origins level with the hashes of namespaces of scripts that come from different origins
            tome_source = os.path.join(origin_folder, "tome_source.json")
            source = None
            if os.path.exists(tome_source):  # Just in case someone put something in the cache without installing
                tome_source = json.loads(load(tome_source))
                source = Source.deserialize(tome_source)
            self._load_commands_from_path(origin_folder, command_type=CommandType.cache, source=source)

    def _load_commands(self):
        self._add_builtin_commands()
        self._add_cache_commands()
        self._add_editable_commands()

    def _add_tome_commands_in_module(
        self, module_path, module_name, package=None, base_folder=None, command_type=None, source=None
    ):
        try:
            if command_type == CommandType.built_in:
                imported_module = importlib.import_module(module_name)
            else:
                # TODO: It would be nice that both used the same import machinery
                old_modules = list(sys.modules.keys())
                full_path = os.path.join(module_path, module_name + ".py")
                spec = importlib.util.spec_from_file_location(module_path, full_path)
                imported_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(imported_module)
                added_modules = set(sys.modules).difference(old_modules)
                for added in added_modules:
                    module = sys.modules[added]
                    if module:
                        try:
                            try:
                                # Most modules will have __file__ != None
                                folder = os.path.dirname(module.__file__)
                            except (AttributeError, TypeError):
                                # But __file__ might not exist or equal None
                                # Like some builtins and Namespace packages py3
                                folder = module.__path__._path[0]
                        except AttributeError:  # In case the module.__path__ doesn't exist
                            pass
                        else:
                            if folder.startswith(module_path):
                                module = sys.modules.pop(added)
                                sys.modules["%s.%s" % (module_path, added)] = module
        except ModuleNotFoundError as e:
            # In case the import fails, to be able to store the command with error defined. It shouldn't be cached
            # so it is re-loaded every time, in case a fix was done like installing requirements

            def _get_tome_command_decorators(file_path):
                ret = []
                with open(file_path) as file:
                    node = ast.parse(file.read())
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            for decorator in child.decorator_list:
                                if (
                                    isinstance(decorator, ast.Call)
                                    and getattr(decorator.func, 'id', '') == 'tome_command'
                                ):
                                    # Check if 'parent' argument is in the decorator
                                    if not any(arg.arg == 'parent' for arg in decorator.args):
                                        commandname = child.name.replace("_", "-")
                                        ret.append(commandname)
                return ret

            filepath = os.path.join(module_path, module_name.replace(".", "/") + ".py")
            command_names = _get_tome_command_decorators(filepath)

            for command_name in command_names:
                fullname = f"{package}:{command_name}"
                doc = f"🚨 Loading command failed: {str(e)}"
                command_info = CommandInfo(
                    package, command_name, doc, command_type, module_name, base_folder, error=str(e), source=source
                )
                self._commands[fullname] = command_info
            raise TomeException(str(e))
        else:
            for item_name in dir(imported_module):
                item = getattr(imported_module, item_name)
                if isinstance(item, TomeCommand) and item.parent is None:
                    self._register_command(item, package, module_name, base_folder, command_type, source=source)

    def _register_command(self, command, package, module_name=None, base_folder=None, command_type=None, source=None):
        fullname = f"{package}:{command.name}" if package else command.name
        command.namespace = package or ""
        command.type = command_type  # setting the command_type
        command.base_folder = base_folder
        command.module_name = module_name
        command_info = CommandInfo(
            command.namespace,
            command.name,
            command.doc,
            command_type,
            module_name,
            base_folder,
            command,
            source=source,
        )
        if base_folder:
            venv_path = os.path.join(base_folder, ".tome_venv")
            if os.path.exists(venv_path):
                command_info.env_path = venv_path

        self._commands[fullname] = command_info

    def _print_similar(self, command):
        """
        Looks for similar commands and prints them if found.
        """
        output = TomeOutput()
        matches = get_close_matches(word=command, possibilities=self._commands.keys(), n=5, cutoff=0.75)

        if len(matches) == 0:
            return

        if len(matches) > 1:
            output.info("The most similar commands are: ")
        else:
            output.info("The most similar command is: ")

        output.info(", ".join(matches))

    def _output_help_cli(self):
        """
        Prints a summary of all the built-in commands.
        """
        output = TomeOutput()

        built_in_commands = [cmd_info for cmd_info in self._commands.values() if cmd_info.type == CommandType.built_in]

        print_grouped_commands({None: {None: built_in_commands}})
        output.info("\nType 'tome <command> -h' for help\n")

    def run(self, *args):
        """Entry point for executing commands, dispatcher to class
        methods
        """
        output = TomeOutput()
        self._load_commands()

        if not args:
            self._output_help_cli()
            return

        try:
            command_argument = args[0][0]
        except IndexError:  # No parameters
            self._output_help_cli()
            return

        if command_argument in ["-v", "--version"]:
            from importlib import metadata

            TomeOutput().info(metadata.version('tomescripts'))
            return

        if command_argument in ["-h", "--help"]:
            self._output_help_cli()
            return

        command_info = self._commands.get(command_argument)
        if command_info and command_info.error:
            raise TomeException(
                f"There was an error when installing the '{command_argument}' command: {command_info.error}. Please check the error and install again."
            )

        command = command_info.command if command_info else None
        if not command:
            output.info(f"'{command_argument}' is not a tome command. See 'tome --help'.")
            output.info("")
            self._print_similar(command_argument)
            raise TomeException(f"Unknown command {command_argument}")

        try:
            command.run(self._tome_api, args[0][1:])
        except Exception:
            raise

    @staticmethod
    def exception_exit_error(exception):
        output = TomeOutput()
        if exception is None:
            return SUCCESS
        if isinstance(exception, TomeException):
            output.error(str(exception))
            return ERROR_GENERAL
        if isinstance(exception, SystemExit):
            if exception.code != 0:
                output.error(f"Exiting with code: {exception.code}")
            return exception.code

        if isinstance(exception, Exception):
            output.error(traceback.format_exc())
            msg = exception_message_safe(exception)
            output.error(msg)
            return ERROR_UNEXPECTED
        else:
            return ERROR_UNEXPECTED


def main(args=None):
    """main entry point of the tome application, using a Command to
    parse parameters

    Exit codes for tome command:

    0: Success (done)
    1: General TomeException error (done)
    2: Ctrl+C
    3: Ctrl+Break
    4: SIGTERM
    """
    if args is None:
        args = sys.argv[1:]

    try:
        tome_api = TomeAPI()
    except TomeException as e:
        sys.stderr.write(f"Error in tome initialization: {e}")
        sys.exit(ERROR_GENERAL)

    def ctrl_c_handler(_, __):
        TomeOutput().info('You pressed Ctrl+C!')
        sys.exit(USER_CTRL_C)

    def sigterm_handler(_, __):
        TomeOutput().info('Received SIGTERM!')
        sys.exit(ERROR_SIGTERM)

    def ctrl_break_handler(_, __):
        TomeOutput().info('You pressed Ctrl+Break!')
        sys.exit(USER_CTRL_BREAK)

    signal.signal(signal.SIGINT, ctrl_c_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)

    if sys.platform == 'win32':
        signal.signal(signal.SIGBREAK, ctrl_break_handler)

    cli = Cli(tome_api)
    error = SUCCESS
    try:
        cli.run(args)
    except BaseException as e:
        error = cli.exception_exit_error(e)
    sys.exit(error)


if __name__ == "__main__":
    main(sys.argv[1:])
