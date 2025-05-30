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

Our subcommands currently return dictionaries. To present this data to the user
in a readable way, or as structured data like JSON, we use **formatters**.

Let's define formatters for our `list` subcommand. We'll add a text formatter
and a JSON formatter.

Modify `utils/todo.py` to include these formatter functions and update the
`@tome_command` decorator for `list`:

```python
Codigo con solo añadidos los formatters
```

**Key changes for formatters:**

- Each subcommand function (`add`, `list`, `done`, `remove`) now `return`s a
  dictionary.
- We defined formatter functions (`todo_list_text_formatter`,
  `todo_list_json_formatter`, `simple_message_text_formatter`,
  `simple_message_json_formatter`).
- The `@tome_command()` decorator for each subcommand was updated with the
  `formatters` argument.
- **tome** now automatically adds a `--format` option to these subcommands.


## 6. Installing and Running the Enhanced `todo` Command

1.  **Save `utils/todo.py`**.
2.  If you haven't already, install your **Tome** from the `my-scripts`
    directory:

        $ tome install . -e

3.  Now, try out your `todo` command and its subcommands:

```console
$ tome utils:todo add "Buy groceries"
Task 'Buy groceries' added with ID 1.

$ tome utils:todo add "Read Tome documentation"
Task 'Read Tome documentation' added with ID 2.

$ tome utils:todo list
Your To-Do List:
    1. [ ] Buy groceries
    2. [ ] Read Tome documentation

$ tome utils:todo done 1
Task 1 marked as done.

$ tome utils:todo list --format json
{
    "status": "success",
    "tasks": [
        {
            "id": 1,
            "description": "Buy groceries",
            "done": true
        },
        {
            "id": 2,
            "description": "Read Tome documentation",
            "done": false
        }
    ]
}

$ tome utils:todo remove 1
Task 1 removed.

$ tome utils:todo list
Your To-Do List:
    1. [ ] Read Tome documentation

$ tome utils:todo done 5 --format json # Example of an error in JSON
{
    "status": "error",
    "error": "Task ID 5 not found."
}
Error: Task ID 5 not found.
```

## Conclusion

In this guide, you've seen how to:
* Structure commands using **subcommands** for better organization.
* Make your commands return data and use **formatters** for flexible text and
  JSON output.
* Utilize the **`tome_api.store.folder`** for persistent data storage.

These features allow you to build more sophisticated and user-friendly
command-line tools with **tome**. Explore the [Python Scripting API
Reference](../reference/python_api.md) for more details on these and other
capabilities.
