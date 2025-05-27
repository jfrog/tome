# Python Scripting API Reference

This section details the Application Programming Interface (API) that **tome**
provides for developers creating custom **Commands** using Python.

## `@tome_command()` Decorator

The primary way to register a Python function as a runnable **tome** **Command**
is by using the `@tome_command()` decorator.

    from tome.command import tome_command

    @tome_command(parent=None, formatters=None)
    def my_command_function(tome_api, parser, *args):
        # Your command logic here
        pass

**Parameters:**

* `parent` (optional): If this command is a subcommand, set this to the parent
  command's function object. Default: `None`.
    * *Example and further details in [Guides: Creating
      Subcommands](../guides/first_script.md#creating-subcommands) (Ajusta este
      enlace si es necesario).*
* `formatters` (optional): A dictionary mapping format names (strings) to
  formatter functions. Each formatter function takes the data returned by your
  command function and handles its presentation.
    * *Example and further details in [Guides: Output
      Formatters](../guides/first_script.md#enhancing-output-with-formatters)
      (Ajusta este enlace si es necesario).*

## Command Function Signature

Python functions decorated with `@tome_command()` are expected to have the
following signature:

    def command_name(tome_api, parser, *args):
        # ...

**Parameters Injected by `tome`:**

* `tome_api`: An instance of `TomeAPI`. This object provides access to
  **tome**'s internal features and APIs that your script might need. Key
  attributes include:
    * `tome_api.vault`: Access to the **tome** vault for managing secrets (see
      [Vault API](#vault-api)).
    * `tome_api.store.folder`: Path to a dedicated local storage folder for your
      **Tome** (see [Store API](#store-api)).
    * *(Add any other relevant `TomeAPI` attributes/methods here).*
* `parser`: An instance of `argparse.ArgumentParser` (or a `TomeArgumentParser`
  subclass). Use this object to define command-line arguments and options for
  your command using standard `argparse` methods like `parser.add_argument()`.
* `*args`: A tuple containing the command-line arguments passed by the user
  after the command name itself. These are typically processed by `parsed_args =
  parser.parse_args(*args)`.

## Argument Parsing (`parser`)

Within your command function, use the provided `parser` object just like you
would with Python's standard `argparse` module to define expected arguments:

    parser.add_argument('filename', help="The file to process.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output.")
    parser.add_argument('--count', type=int, default=1, help="Number of times to do something.")

    parsed_args = parser.parse_args(*args)

    # Access arguments via parsed_args.filename, parsed_args.verbose, etc.

## `TomeOutput` Utility

For producing console output (informational messages, errors, warnings, JSON),
it's highly recommended to use the `TomeOutput` class. This ensures consistent
output style and respects **tome**'s verbosity settings (`-v`, `-q`).

    from tome.api.output import TomeOutput

    output = TomeOutput()
    output.info("This is an informational message.")
    output.error("This is an error message.")
    output.warning("This is a warning.")

    data_for_json = {"key": "value", "items": [1, 2, 3]}
    json_output = TomeOutput(stdout=True) # For data output that should go to stdout
    json_output.print_json(json.dumps(data_for_json, indent=4))

## Output Formatters

If your command function `return`s data (typically a dictionary or a simple
string/list), you can define formatters to present this data in different ways
(e.g., human-readable text, JSON).

Formatters are functions that take one argument (the data returned by your
command) and use `TomeOutput` to print it. They are registered in the
`@tome_command` decorator.

    # In your script:
    def my_text_formatter(data):
        TomeOutput(stdout=True).info(f"Result: {data.get('result')}")

    def my_json_formatter(data):
        import json
        TomeOutput(stdout=True).print_json(json.dumps(data, indent=2))

    @tome_command(formatters={"text": my_text_formatter, "json": my_json_formatter})
    def my_data_command(tome_api, parser, *args):
        # ... logic ...
        return {"result": "some_value", "details": "more_info"}

Users can then select the output format using the automatically added `--format`
flag: `$ tome yournamespace:my_data_command --format json`

## Vault API (Accessing Secrets)
*(Details on `tome_api.vault.open()`, `vault.read()`, `vault.create()`, etc.,
available to scripts).* This section will explain how scripts can interact with
**tome**'s vault functionality.

## Store API (Local Storage)
*(Details on using `tome_api.store.folder` to read/write persistent files
related to a **Tome**).* This section will describe how scripts can utilize the
local storage area provided by **tome**.
