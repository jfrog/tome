# Creating Your First Script

This guide details how to create a new **tome** script from scratch, focusing on
Python scripts. You'll learn about the basic structure, defining arguments, and
how **tome** recognizes your commands.

## Prerequisites

* **tome** is installed. See the [Installation
  Guide](../overview/installing.md).
* You have a directory ready for your new **Tome**. If not, create one and `cd`
  into it.

## 1. Generating a Script with `tome new`

The easiest way to start is with the `tome new` command. This **Tome Command**
scaffolds a new Python script and a basic test file.

    $ tome new example:mycommand

This creates `example/mycommand.py` and `example/tests/test_mycommand.py`.

## 2. Anatomy of a **tome** Python Script

Open `example/mycommand.py`. You'll see something like this:

    from tome.command import tome_command
    from tome.api.output import TomeOutput

    @tome_command()
    def mycommand(tome_api, parser, *args):
        """
        Description of the command.
        """
        parser.add_argument('positional_argument', help="Placeholder for a positional argument")
        parser.add_argument('--optional-argument', help="Placeholder for an optional argument")
        parsed_args = parser.parse_args(*args)

        output = TomeOutput()
        output.info(f"Command 'mycommand' called with {parsed_args.positional_argument}")
        if parsed_args.optional_arg:
            output.info(f"Optional argument: {parsed_args.optional_arg}")

Key parts:
- **`from tome.command import tome_command`**: Imports the necessary decorator.
- **`@tome_command()`**: Decorator that registers the function `mycommand` as a
  **tome** **Command**. The name of the function (with underscores replaced by
  hyphens) becomes the command name within its **Namespace**.
- **`def mycommand(tome_api, parser, *args):`**: The standard signature.
    - `tome_api`: Access to **tome**'s API (e.g., for vault, store).
    - `parser`: An `argparse.ArgumentParser` instance to define command-line
      arguments.
    - `*args`: Raw command-line arguments passed to the script.
- **Docstring**: Becomes the help text for the command.
- **`parser.add_argument(...)`**: Standard `argparse` for defining CLI options.
- **`TomeOutput()`**: Recommended for printing messages.

## 3. Creating Subcommands

To create a command with subcommands (e.g., `tome mycommand subaction`):

    from tome.command import tome_command
    from tome.api.output import TomeOutput

    @tome_command()
    def mycommand(tome_api, parser, *args):
        """Main command description."""
        # Parent command usually doesn't parse args if it only delegates to subcommands
        TomeOutput().info("mycommand needs a subcommand, e.g., 'action1'")

    @tome_command(parent=mycommand)
    def action1(tome_api, parser, *args):
        """Description for action1."""
        parsed_args = parser.parse_args(*args)
        TomeOutput().info("Executing action1")

    @tome_command(parent=mycommand)
    def action2(tome_api, parser, *args):
        """Description for action2."""
        parser.add_argument('--option', help='An option for action2')
        parsed_args = parser.parse_args(*args)
        TomeOutput().info(f"Executing action2 with option: {parsed_args.option}")

## 4. Making Your Script Usable

After writing or modifying your script(s):
1.  Ensure your script files are within a directory that will act as the
    **Namespace** (e.g., `example/mycommand.py`).
2.  From the root of your **Tome** (the directory containing your namespace
    folders, e.g., where you ran `tome new`), run:

        $ tome install . -e

This installs your current directory as an editable **Tome**, making
`example:mycommand` and its subcommands available.
