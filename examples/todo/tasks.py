import os
from tome.command import tome_command
from tome.api.output import TomeOutput


@tome_command()
def tasks(tome_api, parser, *args):
    """Manage your to-do list tasks."""


@tome_command(parent=tasks)
def add(tome_api, parser, *args):
    """Add a new task to the to-do list."""
    parser.add_argument("task", help="The task to add to the to-do list.")
    args = parser.parse_args(*args)

    store_path = tome_api.store.folder
    tasks_file = os.path.join(store_path, "tasks.txt")

    # Create the store directory if it does not exist
    os.makedirs(store_path, exist_ok=True)

    # Append the new task to the tasks file
    with open(tasks_file, "a") as file:
        file.write(args.task + "\n")

    tome_output = TomeOutput()
    tome_output.info(f"Task added: {args.task}")


@tome_command(parent=tasks)
def remove(tome_api, parser, *args):
    """Remove a task from the to-do list."""
    parser.add_argument("task_number", type=int, help="The number of the task to remove.")
    args = parser.parse_args(*args)

    store_path = tome_api.store.folder
    tasks_file = os.path.join(store_path, "tasks.txt")

    tome_output = TomeOutput()

    if not os.path.exists(tasks_file):
        tome_output.error("No tasks found.")
        return

    with open(tasks_file, "r") as file:
        tasks = file.readlines()

    if 0 < args.task_number <= len(tasks):
        removed_task = tasks.pop(args.task_number - 1)
        with open(tasks_file, "w") as file:
            file.writelines(tasks)
        tome_output.info(f"Removed task: {removed_task.strip()}")
    else:
        tome_output.error("Invalid task number.")


@tome_command(parent=tasks)
def list(tome_api, parser, *args):
    """List all tasks in the to-do list."""
    store_path = tome_api.store.folder
    tasks_file = os.path.join(store_path, "tasks.txt")

    tome_output = TomeOutput()

    if not os.path.exists(tasks_file):
        tome_output.info("No tasks found.")
        return

    with open(tasks_file, "r") as file:
        tasks = file.readlines()

    if tasks:
        tome_output.info("To-Do List:")
        for i, task in enumerate(tasks, start=1):
            tome_output.info(f"{i}. {task.strip()}")
    else:
        tome_output.info("No tasks found.")
