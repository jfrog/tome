# Persistent Data Storage with Tome Store

Many **tome** **Commands** need to save information between runs – perhaps user
preferences, cached data, logs, or application-specific files. Instead of
hardcoding file paths or scattering data across the user's system, **tome**
provides a dedicated **Store** feature for this purpose.

The `tome_api` object, passed to your Python command functions, has an attribute
`tome_api.store.folder`. This attribute contains the absolute path to a
directory within the **tome** home (typically `~/.tome/storage/`) where your
scripts can reliably read and write files.

## How to Use `tome_api.store.folder`

Let's illustrate with an example. Imagine a command that counts how many times
it has been executed.

### Example: A Simple Execution Counter

We'll create a command `stats:runcount` that increments a counter each time it's
run and displays the current count.

1.  **Setup the Script:** First, create the script using `tome new`:

    ```console
    $ mkdir my-tome
    $ cd my-tome
    $ tome new stats:runcount --description "Counts and displays how many times it has been run."
    $ tome install . -e
    ```

2.  **Implement `stats/runcount.py`:**

    ```python
    # stats/runcount.py
    from tome.command import tome_command
    from tome.api.output import TomeOutput
    import json
    import os

    COUNTER_FILENAME = "run_counter.json"

    @tome_command()
    def runcount(tome_api, parser, *args):
        """Counts and displays how many times this command has been run."""
        parsed_args = parser.parse_args(*args) # Process any potential future args
        output = TomeOutput(stdout=True)

        # Define a path for this command's data within the tome store
        command_storage_dir = os.path.join(tome_api.store.folder, "stats_runcount")
        os.makedirs(command_storage_dir, exist_ok=True) # Ensure the directory exists
        counter_file_path = os.path.join(command_storage_dir, COUNTER_FILENAME)

        count = 0
        # Load existing count
        if os.path.exists(counter_file_path):
            try:
                with open(counter_file_path, 'r') as f:
                    data = json.load(f)
                    count = data.get("run_count", 0)
            except (IOError, json.JSONDecodeError):
                # If file is corrupt or unreadable, start count from 0
                TomeOutput().warning(f"Could not read counter file, resetting count.")
                count = 0

        # Increment count
        count += 1

        # Save new count
        try:
            with open(counter_file_path, 'w') as f:
                json.dump({"run_count": count}, f)
            output.info(f"This command has been run {count} time(s).")
            output.info(f"(Counter data stored in: {counter_file_path})")
        except IOError as e:
            TomeOutput().error(f"Could not save run count: {e}")
            output.info(f"Current run (not saved) would be #{count}.")
    ```

3.  **Running the Command:** Each time you run the command, the count should
    increment:

    ```console
    $ tome stats:runcount
    This command has been run 1 time(s).
    (Counter data stored in: /<tome_home>/storage/stats_runcount/run_counter.json)

    $ tome stats:runcount
    This command has been run 2 time(s).
    (Counter data stored in: /<tome_home>/storage/stats_runcount/run_counter.json)

    $ tome stats:runcount
    This command has been run 3 time(s).
    (Counter data stored in: /<tome_home>/storage/stats_runcount/run_counter.json)
    ```

    You can inspect the `run_counter.json` file in the specified path to see the
    stored count.

### Best Practices for Using the Store API

* **Organize with Subdirectories:** As shown, create subdirectories within
  `tome_api.store.folder` (e.g., based on your **Namespace** and/or **Command**
  name like `os.path.join(tome_api.store.folder, "your_namespace",
  "your_command")`). This prevents file naming conflicts if multiple **Tomes**
  or **Commands** use the store.
* **Handle File I/O Errors:** Always wrap file operations (reading, writing) in
  `try...except IOError` blocks to manage potential issues gracefully.
* **Inform Users (If Necessary):** If your command stores significant data or
  user-configurable files, consider documenting where this data is located
  (i.e., within the **tome** store) so users can understand, manage, or back it
  up if needed.
