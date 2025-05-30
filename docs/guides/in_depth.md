# Tome Scripts In-Depth

Now that you've seen the basics of creating and running a simple command in the
[Quickstart](../overview/quickstart.md), this guide dives deeper into building
more structured and powerful **tome** commands with Python.

We'll explore how to:

* Organize related actions using **subcommands**.
* Create flexible output presentations with **formatters**.
* Persist and retrieve data using **tome**'s **Store API**.

## 1. The `utils:todo` command and its subcommands

For this guide, we'll build a simple command-line To-Do list manager called
`utils:todo` the will have several subcommands to allow us to:

* `tome utils:todo add`: Add new tasks.
* `tome utils:todo list`: List existing tasks.
* `tome utils:todo mark`: Mark tasks as done.
* `tome utils:todo remove`: Remove tasks.

## 2. Setting Up the Script

First, if you haven't already, create a directory for your project (e.g.,
`my-scripts`) and navigate into it. Then, use `tome new` to create the initial
script for the `todo` command within a `utils` namespace. The main function can
be named `todo`.

```console
$ mkdir my-scripts
$ cd my-scripts
$ tome new utils:todo
Generated script: utils/todo.py
```

Also install it as editable at this point so we can check our changes as we
introduce them.

```console
$ tome install . -e
Configured editable installation for ...
Installed source: ...
```

## 3. Implementing Subcommands

Let's edit `utils/todo.py`. Let's start by defining the main `todo` command and
its first subcommand, `add`. For data persistence, we'll use a simple JSON file
stored via [tome's Store API](features/store.md).

```python
from tome.command import tome_command
from tome.api.output import TomeOutput

@tome_command()
def todo(tome_api, parser, *args):
    """
    A simple command-line To-Do list manager.
    """
    pass

@tome_command(parent=todo)
def add(tome_api, parser, *args):
    """Adds a new task to the list."""
    parser.add_argument('description', help="The description of the task.")
    parsed_args = parser.parse_args(*args)

    TomeOutput(stdout=True).info(f"Task '{parsed_args.description}' added (not saved yet).")
```

**Explanation of Subcommand Structure:**

* The main `todo` function is decorated with `@tome_command()` but just declares
  a `pass` because it takes no arguments it's just the entry point for the
  subcommands.
* The `add` subcommand is decorated with
  `@tome_command(parent=todo)`, making it subcommands of `todo`.
* The `add` subcommand defines its own arguments using the `parser` object it
  receives.

At this point this does not do much:

```console
$ tome utils:todo add "Buy groceries"
Task 'Buy groceries' added (not saved).
```

Let's make some improvements:

## 4. Using the Store API (`tome_api.store.folder`)

Hemos hecho el subcomando pero realmente no hace mucho, en este paso explicamos
como podemos tener el store api para un sitio centralizado donde guardar
información esto tiene la ventaja de que pueda see compartida entre varios
comandos instalados por ej.

```python

from tome.command import tome_command
from tome.api.output import TomeOutput
import json
import os

TASKS_FILE_NAME = "mytasks.json"

@tome_command()
def todo(tome_api, parser, *args):
    """
    A simple command-line To-Do list manager.
    """
    pass

@tome_command(parent=todo)
def add(tome_api, parser, *args):
    """Adds a new task to the list."""
    parser.add_argument('description', help="The description of the task.")
    parsed_args = parser.parse_args(*args)

    task_description = parsed_args.description

    utility_storage_path = os.path.join(tome_api.store.folder, "utils_todo")
    os.makedirs(utility_storage_path, exist_ok=True)
    tasks_file_path = os.path.join(utility_storage_path, TASKS_FILE_NAME)

    tasks = []
    if os.path.exists(tasks_file_path):
        try:
            with open(tasks_file_path, 'r') as f:
                tasks = json.load(f)
        except (json.JSONDecodeError, IOError):
            tasks = []

    new_task = {"description": task_description}
    tasks.append(new_task)

    try:
        with open(tasks_file_path, 'w') as f:
            json.dump(tasks, f, indent=2)

        TomeOutput(stdout=True).info(f"Task '{task_description}' saved in '{tasks_file_path}'.")
    except IOError:
        TomeOutput().error(f"Could not save task to '{tasks_file_path}'.")
```

Explicar lo que se ha hecho, puede que reutilizar algo de esto:

This provides a consistent, managed directory within
your **tome** home (usually `~/.tome/storage/`) where your application can store
data.

* **`os.path.join(tome_api.store.folder, TASKS_FILE)`**: Constructs a path to
  `tasks.json` inside the dedicated store folder.
* **`os.makedirs(tome_api.store.folder, exist_ok=True)`**: Ensures the main
  store folder exists.

Now we have persistent information:

```console
$ tome utils:todo add "Buy groceries"
Task 'Buy groceries' saved in '~/.tome/storage/utils_todo/mytasks.json'.

$ cat '~/.tome/storage/utils_todo/mytasks.json'
[
  {
    "description": "Buy groceries"
  }
]
```

This is a clean way to handle persistent data for your commands without
hardcoding paths or worrying about where to put user-specific data.

## 5. Standarazing Output using Formatters

Our subcommands currently is printing a success message to `stdout` but **tome**
provides a way of presenting information in a more structured? way using
`formatters`.  Let's define formatters for our `list` subcommand. We'll add a
`text` formatter and a `JSON` formatter.

Modify `utils/todo.py` to include these formatter functions and update the
`@tome_command` decorator for `list`:

```python
from tome.command import tome_command
from tome.api.output import TomeOutput
from tome.errors import TomeException
import json
import os

TASKS_FILE_NAME = "mytasks.json"

def todo_text_formatter(data_dict):
    if data_dict.get("status") == "success" and "message" in data_dict:
        TomeOutput(stdout=True).info(data_dict["message"])
    elif data_dict.get("status") == "error" and "error" in data_dict:
        raise TomeException(data_dict["error"])

def todo_json_formatter(data_dict):
    TomeOutput(stdout=True).print_json(json.dumps(data_dict, indent=2))

    if data_dict.get("status") == "error" and "error" in data_dict:
        raise TomeException(data_dict["error"])


@tome_command()
def todo(tome_api, parser, *args):
    """
    A simple command-line To-Do list manager.
    """
    pass

@tome_command(parent=todo, formatters={"text": todo_text_formatter, "json": todo_json_formatter})
def add(tome_api, parser, *args):
    """Adds a new task to the list."""
    parser.add_argument('description', help="The description of the task.")
    parsed_args = parser.parse_args(*args)

    task_description = parsed_args.description

    utility_storage_path = os.path.join(tome_api.store.folder, "utils_todo")
    os.makedirs(utility_storage_path, exist_ok=True)
    tasks_file_path = os.path.join(utility_storage_path, TASKS_FILE_NAME)

    tasks = []
    if os.path.exists(tasks_file_path):
        try:
            with open(tasks_file_path, 'r') as f:
                tasks = json.load(f)
        except (json.JSONDecodeError, IOError):
            tasks = []

    new_task = {"description": task_description}
    tasks.append(new_task)

    try:
        with open(tasks_file_path, 'w') as f:
            json.dump(tasks, f, indent=2)

        return {
            "action": "add",
            "status": "success",
            "message": f"Task '{task_description}' added.",
            "description": task_description
        }
    except IOError as e:
        return {
            "action": "add",
            "status": "error",
            "error": f"Could not save task to '{tasks_file_path}': {str(e)}",
            "description": task_description
        }
```

**Understanding the Changes:**

- The `@tome_command()` decorator for `add` was updated with a `formatters` argument.
- The `add` function now `return`s a dictionary, whether for success or a
  validation error.
- We defined `todo_text_formatter` and `todo_json_formatter` to handle the dictionary
  returned by `add` you can select which one you want to use when running
  `utils:todo add` with the `--format` argument. The `text` one is used by
  default if the `--format` argument is not passed.
- The `todo_text_formatter` raises a `TomeException` if it finds an error in the
  data, ensuring **tome** reports it.
- The `todo_json_formatter` prints the JSON (which will include the error structure
  if present) and *then* raises `TomeException` if an error key exists, so
  automated tools get structured error data but the script still exits with an
  error code.

Now, **tome** automatically adds a `--format` option to your command.

Try it out:

Default text output:

```console
$ tome utils:todo add "Buy groceries"
Task 'Buy groceries' added.


$ tome utils:todo add "Take the dog out" --format=json
{
  "action": "add",
  "status": "success",
  "message": "Task 'Take the dog out' added.",
  "description": "Take the dog out"
}
```

Using formatters like this keeps your command's core logic separate from its
presentation, making your code cleaner. Plus, you can easily offer different
output styles (e.g., text for users, JSON for tools) from a single command,
making it more maintainable. You can learn more about how to define and use them
in the [Output Formatters
Reference](../reference/python_api.md#output-formatters).

## 6. Finishing the command

You can find the full implementation in the examples folder in the GitHub
repository. Please, [copy and paste from
here](https://github.com/jfrog/tome/blob/main/examples/utils/todo.py) if you
want to test the complete command.

## Conclusion

In this guide, you've seen how to:

* Structure commands using **subcommands** for better organization.
* Utilize the **`tome_api.store.folder`** for persistent data storage.
* Make your commands return data and use **formatters** for flexible text and
  JSON output.
* Tested your command with different arguments and output formats using the
  automatically provided `--format` option.

These features allow you to build more sophisticated and user-friendly
command-line tools with **tome**. Explore the [Python Scripting API
Reference](../reference/python_api.md) for more details on these and other
capabilities.
