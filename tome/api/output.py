# TODO: it's not necessary to use rich here, we can decide how we want the output
from contextlib import nullcontext

from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner


class TomeOutput:
    LEVEL_QUIET = 80  # -q
    LEVEL_DEFAULT = 40  # Default - Most of messages that users might be interested in.
    LEVEL_V = 30  # -v  Detailed informational messages.
    LEVEL_VV = 20  # -vv Closely related to internal implementation details
    LEVEL_VVV = 10  # -vvv Fine-grained messages with very low-level implementation details

    _tome_output_level = LEVEL_DEFAULT

    def __init__(self, stdout=False):
        self._tome_console = Console(stderr=not stdout)

    def status(self, message):
        if self._tome_output_level <= self.LEVEL_DEFAULT:
            self._tome_console.print(message, style="bold blue")

    def error(self, message):
        if self._tome_output_level <= self.LEVEL_DEFAULT:
            self._tome_console.print("Error: " + message, style="bold red")

    def info(self, message):
        if self._tome_output_level <= self.LEVEL_DEFAULT:
            self._tome_console.print(message, style="default")

    def warning(self, message):
        if self._tome_output_level <= self.LEVEL_DEFAULT:
            self._tome_console.print("Warning: " + message, style="bold yellow")

    def verbose(self, message, style=None, verbosity=None):
        verbosity = verbosity or self.LEVEL_V
        if self._tome_output_level <= verbosity:
            self._tome_console.print(message, style=style)

    def print(self, message, verbosity=None):
        verbosity = verbosity or self.LEVEL_DEFAULT
        if self._tome_output_level <= verbosity:
            self._tome_console.print(message, soft_wrap=True, highlight=False)

    def print_json(self, json, verbosity=None):
        verbosity = verbosity or self.LEVEL_DEFAULT
        if self._tome_output_level <= verbosity:
            self._tome_console.print_json(json)

    @classmethod
    def spinner(cls, text="Working..."):
        """Provides a spinner context if verbosity level allows, else a nullcontext."""
        # Normally this is used with tome_run that are the long operations
        # and in those cases tome_run will print the output of the command
        # if we are in verbose mode, so we don't need to print the spinner
        # also do not print if quiet mode is enabled
        if cls.is_verbose() or cls.is_quiet():
            return nullcontext()
        else:
            return Live(Spinner("dots", text=text), transient=True)

    @classmethod
    def define_log_level(cls, verbose_count, quiet):
        if quiet:
            cls._tome_output_level = cls.LEVEL_QUIET  # Only critical errors
        else:
            levels = [cls.LEVEL_DEFAULT, cls.LEVEL_V, cls.LEVEL_VV, cls.LEVEL_VVV]  # Corresponding to verbose levels
            cls._tome_output_level = levels[min(verbose_count, len(levels) - 1)]

    @classmethod
    def get_log_level(cls):
        return cls._tome_output_level

    @classmethod
    def is_quiet(cls):
        return cls._tome_output_level == cls.LEVEL_QUIET

    @classmethod
    def is_verbose(cls):
        return cls._tome_output_level <= cls.LEVEL_V
