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

## 3. Implementing Subcommands

Let's edit `utils/todo.py`. We'll define the main `todo` command and then its
subcommands. For data persistence, we'll use a simple JSON file stored via
[tome's Store API](features/store.md).

```python
# utils/todo.py
from tome.command import tome_command
from tome.api.output import TomeOutput
from tome.errors import TomeException
import json
import os

TASKS_FILE = "tasks.json" # To be stored in tome_api.store.folder

def _load_tasks(tome_api):
    """Helper to load tasks from the store."""
    tasks_path = os.path.join(tome_api.store.folder, TASKS_FILE)
    if not os.path.exists(tasks_path):
        return []
    try:
        with open(tasks_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return [] # Return empty list on error or if file is malformed

def _save_tasks(tome_api, tasks):
    """Helper to save tasks to the store."""
    os.makedirs(tome_api.store.folder, exist_ok=True)
    tasks_path = os.path.join(tome_api.store.folder, TASKS_FILE)
    with open(tasks_path, 'w') as f:
        json.dump(tasks, f, indent=2)

# --- Main 'todo' Command ---
@tome_command()
def todo(tome_api, parser, *args):
    """
    A simple command-line To-Do list manager.
    Use subcommands: add, list, done, remove.
    """
    # This parent command generally doesn't process arguments itself
    # when it has required subcommands. Argparse handles showing help.
    # You could add a default action if no subcommand is called,
    # but for now, we'll rely on subcommands being specified.
    pass

# --- Subcommand: add ---
@tome_command(parent=todo)
def add(tome_api, parser, *args):
    """Adds a new task to the list."""
    parser.add_argument('description', nargs='+', help="The description of the task.")
    parsed_args = parser.parse_args(*args)

    task_description = " ".join(parsed_args.description)
    tasks = _load_tasks(tome_api)

    new_task_id = len(tasks) + 1
    tasks.append({"id": new_task_id, "description": task_description, "done": False})
    _save_tasks(tome_api, tasks)

    # For actions like 'add', we can return a simple confirmation.
    # This will be handled by the formatters.
    return {"status": "success", "message": f"Task '{task_description}' added with ID {new_task_id}."}

# --- Subcommand: list ---
@tome_command(parent=todo) # We'll add formatters to this later
def list(tome_api, parser, *args):
    """Lists all tasks."""
    # No arguments needed for this simple list
    parsed_args = parser.parse_args(*args)

    tasks = _load_tasks(tome_api)
    if not tasks:
        return {"status": "empty", "message": "No tasks yet!"}

    return {"status": "success", "tasks": tasks}

# --- Subcommand: done ---
@tome_command(parent=todo)
def done(tome_api, parser, *args):
    """Marks a task as done."""
    parser.add_argument('task_id', type=int, help="The ID of the task to mark as done.")
    parsed_args = parser.parse_args(*args)

    tasks = _load_tasks(tome_api)
    task_found = False
    for task in tasks:
        if task['id'] == parsed_args.task_id:
            if task['done']:
                return {"status": "no_change", "message": f"Task {parsed_args.task_id} was already done."}
            task['done'] = True
            task_found = True
            break

    if not task_found:
        return {"status": "error", "error": f"Task ID {parsed_args.task_id} not found."}

    _save_tasks(tome_api, tasks)
    return {"status": "success", "message": f"Task {parsed_args.task_id} marked as done."}

# --- Subcommand: remove ---
@tome_command(parent=todo)
def remove(tome_api, parser, *args):
    """Removes a task from the list."""
    parser.add_argument('task_id', type=int, help="The ID of the task to remove.")
    parsed_args = parser.parse_args(*args)

    tasks = _load_tasks(tome_api)
    original_length = len(tasks)
    tasks = [task for task in tasks if task['id'] != parsed_args.task_id]

    if len(tasks) == original_length:
        return {"status": "error", "error": f"Task ID {parsed_args.task_id} not found for removal."}

    # Re-index tasks to keep IDs sequential (optional, but good for this simple example)
    for i, task in enumerate(tasks):
        task['id'] = i + 1

    _save_tasks(tome_api, tasks)
    return {"status": "success", "message": f"Task {parsed_args.task_id} removed."}
```

**Explanation of Subcommand Structure:**

* The main `todo` function is decorated with `@tome_command()`.
* Functions like `add`, `list`, `done`, and `remove` are decorated with
  `@tome_command(parent=todo)`, making them subcommands of `todo`.
* Each subcommand defines its own arguments using the `parser` object it
  receives.
* Notice that all command functions now `return` a dictionary. This is in
  preparation for using formatters.

## 4. Introducing Output Formatters

Our subcommands currently return dictionaries. To present this data to the user
in a readable way, or as structured data like JSON, we use **formatters**.

Let's define formatters for our `list` subcommand. We'll add a text formatter
and a JSON formatter.

Modify `utils/todo.py` to include these formatter functions and update the
`@tome_command` decorator for `list`:

```python
    # (Add to the top of utils/todo.py if not already there)
    # import json
    # from tome.errors import TomeException
    # from tome.api.output import TomeOutput

    # --- Formatter Functions for 'todo list' ---
    def todo_list_text_formatter(data):
        output = TomeOutput(stdout=True)
        if data.get("status") == "empty":
            output.info(data["message"])
            return
        if data.get("status") == "success" and "tasks" in data:
            output.info("Your To-Do List:")
            for task in data["tasks"]:
                status_marker = "[x]" if task.get('done') else "[ ]"
                output.info(f"  {task['id']}. {status_marker} {task['description']}")
        elif "error" in data: # Handle potential errors passed to formatter
            raise TomeException(data["error"])
        else:
            output.warning("Could not display tasks.")

    def todo_list_json_formatter(data):
        output = TomeOutput(stdout=True)
        output.print_json(json.dumps(data, indent=2))
        if "error" in data: # Ensure CLI exits with error if data indicates an error
             raise TomeException(data["error"])

    # ... (keep the _load_tasks, _save_tasks, and main 'todo' command) ...

    # --- Subcommand: add (Formatter for confirmation message) ---
    def simple_message_text_formatter(data):
        output = TomeOutput(stdout=True)
        if "error" in data:
            raise TomeException(data["error"])
        elif "message" in data:
            output.info(data["message"])

    def simple_message_json_formatter(data):
        output = TomeOutput(stdout=True)
        output.print_json(json.dumps(data, indent=2))
        if "error" in data:
            raise TomeException(data["error"])

    @tome_command(parent=todo, formatters={"text": simple_message_text_formatter, "json": simple_message_json_formatter})
    def add(tome_api, parser, *args):
        # ... (keep existing add logic that returns a dictionary) ...
        # Example return: {"status": "success", "message": f"Task '{task_description}' added with ID {new_task_id}."}
        """Adds a new task to the list."""
        parser.add_argument('description', nargs='+', help="The description of the task.")
        parsed_args = parser.parse_args(*args)
        task_description = " ".join(parsed_args.description)
        tasks = _load_tasks(tome_api)
        new_task_id = len(tasks) + 1
        tasks.append({"id": new_task_id, "description": task_description, "done": False})
        _save_tasks(tome_api, tasks)
        return {"status": "success", "message": f"Task '{task_description}' added with ID {new_task_id}."}


    # --- Subcommand: list (Updated with formatters) ---
    @tome_command(parent=todo, formatters={"text": todo_list_text_formatter, "json": todo_list_json_formatter})
    def list(tome_api, parser, *args):
        # ... (keep existing list logic that returns a dictionary) ...
        """Lists all tasks."""
        parsed_args = parser.parse_args(*args)
        tasks = _load_tasks(tome_api)
        if not tasks:
            return {"status": "empty", "message": "No tasks yet!"}
        return {"status": "success", "tasks": tasks}

    # --- Subcommand: done (Updated with formatters) ---
    @tome_command(parent=todo, formatters={"text": simple_message_text_formatter, "json": simple_message_json_formatter})
    def done(tome_api, parser, *args):
        # ... (keep existing done logic that returns a dictionary) ...
        """Marks a task as done."""
        parser.add_argument('task_id', type=int, help="The ID of the task to mark as done.")
        parsed_args = parser.parse_args(*args)
        tasks = _load_tasks(tome_api)
        task_found = False
        for task in tasks:
            if task['id'] == parsed_args.task_id:
                if task['done']:
                    return {"status": "no_change", "message": f"Task {parsed_args.task_id} was already done."}
                task['done'] = True
                task_found = True
                break
        if not task_found:
            return {"status": "error", "error": f"Task ID {parsed_args.task_id} not found."}
        _save_tasks(tome_api, tasks)
        return {"status": "success", "message": f"Task {parsed_args.task_id} marked as done."}


    # --- Subcommand: remove (Updated with formatters) ---
    @tome_command(parent=todo, formatters={"text": simple_message_text_formatter, "json": simple_message_json_formatter})
    def remove(tome_api, parser, *args):
        # ... (keep existing remove logic that returns a dictionary) ...
        """Removes a task from the list."""
        parser.add_argument('task_id', type=int, help="The ID of the task to remove.")
        parsed_args = parser.parse_args(*args)
        tasks = _load_tasks(tome_api)
        original_length = len(tasks)
        tasks = [task for task in tasks if task['id'] != parsed_args.task_id]
        if len(tasks) == original_length:
            return {"status": "error", "error": f"Task ID {parsed_args.task_id} not found for removal."}
        for i, task in enumerate(tasks): # Re-index
            task['id'] = i + 1
        _save_tasks(tome_api, tasks)
        return {"status": "success", "message": f"Task {parsed_args.task_id} removed."}
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

## 5. Using the Store API (`tome_api.store.folder`)

Our `_load_tasks` and `_save_tasks` helper functions are already using
`tome_api.store.folder`. This provides a consistent, managed directory within
your **tome** home (usually `~/.tome/storage/`) where your application can store
data.

* **`os.path.join(tome_api.store.folder, TASKS_FILE)`**: Constructs a path to
  `tasks.json` inside the dedicated store folder.
* **`os.makedirs(tome_api.store.folder, exist_ok=True)`**: Ensures the main
  store folder exists.

This is a clean way to handle persistent data for your commands without
hardcoding paths or worrying about where to put user-specific data.

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
