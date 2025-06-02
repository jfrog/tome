from tome.command import tome_command
from tome.api.output import TomeOutput
from tome.errors import TomeException
import json
import os

TASKS_FILE_NAME = "mytasks.json"


def _get_todo_store_path(tome_api):
    return os.path.join(tome_api.store.folder, "utils_todo")


def _get_tasks_file_path(tome_api):
    return os.path.join(_get_todo_store_path(tome_api), TASKS_FILE_NAME)


def _load_tasks(tome_api):
    tasks_path = _get_tasks_file_path(tome_api)
    if not os.path.exists(tasks_path):
        return []
    try:
        with open(tasks_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_tasks(tome_api, tasks):
    todo_store_path = _get_todo_store_path(tome_api)
    os.makedirs(todo_store_path, exist_ok=True)
    tasks_path = _get_tasks_file_path(tome_api)
    with open(tasks_path, 'w') as f:
        json.dump(tasks, f, indent=2)


def todo_text_formatter(data_dict):
    output = TomeOutput(stdout=True)
    if data_dict.get("status") == "error" and "error" in data_dict:
        raise TomeException(data_dict["error"])
    elif "message" in data_dict:
        output.info(data_dict["message"])
    elif data_dict.get("status") == "success":
        action = data_dict.get("action", "Operation")
        output.info(f"{action.capitalize()} completed successfully.")
    else:
        action = data_dict.get("action", "task operation")
        TomeOutput().warning(f"Formatter received an unclear status for {action}.")


def todo_json_formatter(data_dict):
    output = TomeOutput(stdout=True)
    output.print_json(json.dumps(data_dict, indent=2))
    if data_dict.get("status") == "error" and "error" in data_dict:
        raise TomeException(data_dict["error"])


def todo_list_text_formatter(data_dict):
    output = TomeOutput(stdout=True)
    if data_dict.get("status") == "error" and "error" in data_dict:
        raise TomeException(data_dict["error"])
    elif data_dict.get("status") == "empty":
        output.info(data_dict.get("message", "No tasks found."))
        return

    tasks = data_dict.get("tasks", [])
    if tasks:
        output.info("Your To-Do List:")
        for task in tasks:
            status_marker = "[X]" if task.get('done') else "[ ]"
            output.info(f"  {task.get('id', '?')}. {status_marker} {task.get('description', 'N/A')}")
    else:
        output.info("No tasks to display.")


@tome_command()
def todo(tome_api, parser, *args):
    """
    A simple command-line To-Do list manager.
    Use subcommands: add, list, done, remove.
    """
    pass


@tome_command(parent=todo, formatters={"text": todo_text_formatter, "json": todo_json_formatter})
def add(tome_api, parser, *args):
    """Adds a new task to the list."""
    parser.add_argument('description', nargs='+', help="The description of the task.")
    parsed_args = parser.parse_args(*args)
    task_description = " ".join(parsed_args.description)

    tasks = _load_tasks(tome_api)
    new_task_id = (tasks[-1]['id'] + 1) if tasks and isinstance(tasks[-1], dict) and 'id' in tasks[-1] else 1
    new_task = {"id": new_task_id, "description": task_description, "done": False}
    tasks.append(new_task)

    try:
        _save_tasks(tome_api, tasks)
        return {
            "action": "add",
            "status": "success",
            "message": f"Task '{task_description}' added with ID {new_task_id}.",
            "task_id": new_task_id,
            "description": task_description,
        }
    except IOError as e:
        return {
            "action": "add",
            "status": "error",
            "error": f"Could not save task: {str(e)}",
            "description": task_description,
        }


@tome_command(parent=todo, formatters={"text": todo_list_text_formatter, "json": todo_json_formatter})
def list(tome_api, parser, *args):
    """Lists all tasks."""
    parser.parse_args(*args)
    tasks = _load_tasks(tome_api)
    if not tasks:
        return {"action": "list", "status": "empty", "message": "No tasks yet!", "tasks": []}
    return {"action": "list", "status": "success", "tasks": tasks}


@tome_command(parent=todo, formatters={"text": todo_text_formatter, "json": todo_json_formatter})
def done(tome_api, parser, *args):
    """Marks a task as done by its ID."""
    parser.add_argument('task_id', type=int, help="The ID of the task to mark as done.")
    parsed_args = parser.parse_args(*args)
    tasks = _load_tasks(tome_api)
    task_to_update = next((task for task in tasks if task.get('id') == parsed_args.task_id), None)

    if not task_to_update:
        return {"action": "done", "status": "error", "error": f"Task ID {parsed_args.task_id} not found."}
    if task_to_update.get('done'):
        return {
            "action": "done",
            "status": "no_change",
            "message": f"Task {parsed_args.task_id} ('{task_to_update.get('description')}') was already done.",
        }

    task_to_update['done'] = True
    try:
        _save_tasks(tome_api, tasks)
        return {
            "action": "done",
            "status": "success",
            "message": f"Task {parsed_args.task_id} ('{task_to_update.get('description')}') marked as done.",
        }
    except IOError as e:
        return {"action": "done", "status": "error", "error": f"Could not update task: {str(e)}"}


@tome_command(parent=todo, formatters={"text": todo_text_formatter, "json": todo_json_formatter})
def remove(tome_api, parser, *args):
    """Removes a task by its ID."""
    parser.add_argument('task_id', type=int, help="The ID of the task to remove.")
    parsed_args = parser.parse_args(*args)
    tasks = _load_tasks(tome_api)
    task_to_remove = next((task for task in tasks if task.get('id') == parsed_args.task_id), None)

    if not task_to_remove:
        return {"action": "remove", "status": "error", "error": f"Task ID {parsed_args.task_id} not found for removal."}

    tasks = [task for task in tasks if task.get('id') != parsed_args.task_id]

    try:
        _save_tasks(tome_api, tasks)
        return {
            "action": "remove",
            "status": "success",
            "message": f"Task {parsed_args.task_id} ('{task_to_remove.get('description')}') removed.",
        }
    except IOError as e:
        return {"action": "remove", "status": "error", "error": f"Could not remove task: {str(e)}"}
