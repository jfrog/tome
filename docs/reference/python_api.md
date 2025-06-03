# Python API Reference

This section provides detailed information for developers creating custom
**tome** **Commands** using Python.

## `@tome_command()` Decorator

The `@tome_command()` decorator is the primary mechanism for registering a
Python function as a runnable **tome** **Command**. It tells **tome** that your
function should be discoverable and executable through the CLI.

```python
from tome.command import tome_command

@tome_command(parent=None, formatters=None)
def my_command_function(tome_api, parser, *args):
    # Your command logic here
    pass
```

**Parameters:**

* `parent` (optional, default: `None`): If this command is intended to be a
  subcommand of another **tome** **Command**, set this parameter to the function
  object of the parent command. This enables a hierarchical command structure
  (e.g., `tome maincommand subcommand`). For a practical example, see the
  "[Building Commands with
  Subcommands](../guides/in_depth.md#3-implementing-subcommands)" section in our
  In-Depth guide.

* `formatters` (optional, default: `None`): A dictionary that maps output format
  names (strings, e.g., `"text"`, `"json"`) to Python functions that will handle
  the presentation of data returned by your command. When formatters are
  defined, **tome** automatically adds a `--format` option to your command.
  Learn more in the "[Standardizing Output using
  Formatters](../guides/in_depth.md#5-standarazing-output-using-formatters)"
  section of the In-Depth guide and in the [Output
  Formatters](#output-formatters) section below.

Python functions decorated with `@tome_command()` must follow a specific
signature to correctly receive information and tools from **tome**:

```python
def your_command_name(tome_api, parser, *args):
    # Command implementation
    # ...
```

**Parameters Injected by `tome`:**

* `tome_api` (`TomeAPI` instance): This object is your script's gateway to
    **tome**'s core functionalities. Key attributes include:

    * `tome_api.vault`: Provides access to the **tome** Vault for secure secret
      management. (See [Vault API](#vault-api-for-scripts) below).

    * `tome_api.store.folder` (string): The absolute path to a dedicated local
      storage directory for the current **Tome**, where your script can
      read/write persistent data. (See [Store API](#store-api-for-scripts)
      below).

* `parser` (`TomeArgumentParser` instance): An instance of an
    `argparse.ArgumentParser` subclass. Use this object to define the
    command-line arguments and options that your **Command** accepts, using
    standard `argparse` methods like `parser.add_argument()`.

* `*args` (tuple): A tuple containing the raw command-line arguments passed by
    the user after the **Command**'s name (and any subcommand names). These are
    typically processed by calling `parsed_args = parser.parse_args(*args)`.

## Argument Parsing (using `parser`)

Within your command function, use the provided `parser` object as you would with
Python's standard `argparse` library to define how your command accepts input:

```python
# Example within your command function:
parser.add_argument('filename', help="The path to the file to process.")
parser.add_argument('--lines', type=int, default=10, help="Number of lines to display (default: 10).")
parser.add_argument('--verbose', '-v', action='store_true', help="Enable verbose output.")

parsed_args = parser.parse_args(*args)

# You can then access the values:
# file_to_process = parsed_args.filename
# num_lines = parsed_args.lines
# if parsed_args.verbose:
#     print("Verbose mode enabled.")
```

## `TomeOutput`

For producing console output (informational messages, errors, warnings, or
structured data like JSON), it is highly recommended to use the `TomeOutput`
class from `tome.api.output`. This utility ensures that your command's output is
consistent with **tome**'s overall style and respects its verbosity settings
(controlled by `-v` or `-q` flags).

```python
from tome.api.output import TomeOutput
import json # For print_json example

# General messages (typically go to stderr by default)
output = TomeOutput()
output.info("This is an informational message.")
output.error("This is an error message.")
output.warning("This is a warning.")

# For primary command output (e.g., results, data - typically to stdout)
data_output = TomeOutput(stdout=True)
data_for_json = {"key": "value", "items": [1, 2, 3]}
data_output.print("This is the main result of the command.")
data_output.print_json(json.dumps(data_for_json, indent=2))
```

**Note on `stdout` vs. `stderr`:** By default, `TomeOutput()` directs its
messages (like `.info()`, `.warning()`, `.error()`) to `stderr`. This is a
common practice for diagnostic and informational messages in CLI tools,
reserving `stdout` for the primary data output of a command (which might be
piped to other tools). If your command's main result is textual, use
`TomeOutput(stdout=True).print()` or `TomeOutput(stdout=True).info()` for that
specific output. Formatter functions also typically use
`TomeOutput(stdout=True)`.

## Output Formatters

When a **Command** needs to present its results in multiple formats (e.g.,
human-readable text, JSON for scripts), **tome**'s formatter system provides a
clean solution. Instead of the command function printing directly, it `return`s
data (usually a dictionary). Formatter functions, registered via the
`formatters` argument in `@tome_command`, then handle the presentation. This way
we have several advantages:

* **Separation of Concerns:** Command logic (processing data) is decoupled from
  presentation logic (displaying data). This leads to cleaner, more maintainable
  code.
* **Flexible Output:** Offer multiple output formats (text, JSON, YAML, etc.)
  from a single command logic, catering to different users or automation needs.
* **Consistency:** Standardize how data and errors are presented across
  different commands.

**Defining and Using Formatters:**

1.  **Command Function Returns Data:** Your command function should return a
    dictionary (or other serializable data).

```python
@tome_command(formatters={"text": my_text_formatter, "json": my_json_formatter})
def my_data_command(tome_api, parser, *args):
    # ... process and gather data ...
    result_data = {"item_name": "Example", "value": 42, "status": "success"}
    return result_data
```

2.  **Create Formatter Functions:** Each formatter is a Python function that
    accepts one argument (the data dictionary returned by your command) and uses
    `TomeOutput` to print it.

```python
# In your script:
def my_text_formatter(data):
    TomeOutput(stdout=True).info(f"Item: {data.get('item_name')}, Value: {data.get('value')}")

def my_json_formatter(data):
    import json
    TomeOutput(stdout=True).print_json(json.dumps(data, indent=2))
```

If the data dictionary contains an error (e.g., `{"status": "error",
"error": "Something went wrong"}`), your formatter should typically raise a
`TomeException(data["error"])` so **tome** can handle the error reporting
and exit code appropriately.

Users can then select an output format: `$ tome yournamespace:my_data_command
--format json`

If `--format` is not provided, **tome** will attempt to use a formatter named
`"text"` by default.

## Error Handling

To signal operational errors from your **Command** or formatters, `raise
TomeException` from `tome.errors`.

    ```python
    from tome.errors import TomeException
    # if error_condition:
    #     raise TomeException("Specific error description.")
    ```

**tome** will catch these exceptions, print a standardized error message to
`stderr`, and exit with a non-zero status code (typically `1`).

## Vault API (for Scripts)

Access secrets via `tome_api.vault` (an instance of `VaultApi`).

**`tome_api.vault` Methods:**

* `open(name='default', password=None) -> Vault`: Opens a vault. Raises
  `TomeException` on failure.
* `create(name, password)`: Creates a new vault.
* `list() -> dict`: Lists vaults and their secret names/descriptions.

**`Vault` Instance Methods:**

* `my_vault.read(name: str) -> str | None`: Reads a secret's value.
* `my_vault.create(name, text, description=None, update=False) -> State`:
  Adds/updates a secret.
* `my_vault.delete(name: str)`: Deletes a secret.
* `my_vault.list() -> list`: Lists secrets (name, description) in the opened
  vault.

*See the [Vault Guide](../guides/features/vault.md) for full examples.*

## Store API (for Scripts)

Access a persistent local storage directory via `tome_api.store.folder` (string
path, typically `~/.tome/storage/`). Use this for script-specific
configurations, caches, or data files.

*See the [Store Guide](../guides/features/store.md) for practical examples.*
