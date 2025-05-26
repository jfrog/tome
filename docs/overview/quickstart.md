# Quickstart: Your First 5 Minutes with Tome

This guide will get you from zero to running your own custom script in about 5
minutes. We'll create a simple script, install it with tome as editable so we
can make live changes to it and run it.

Throughout this guide, you will encounter several terms specific to **tome**.
For detailed definitions, we invite you to review our
[Glossary](../resources/glossary.md).

## Step 1: Initialize Your Script Collection (Your "Tome")

First, let's create a dedicated directory for our scripts. This directory will
represent your personal **Tome** or collection of scripts.

```console
$ mkdir my-scripts
$ cd my-scripts
```

Now, let's tell **tome** to create a new script within this collection. We'll
create a script in the `utils` namespace called `datetime`.

```console
$ tome new utils:datetime
```

This command will generate a couple of files for you:

* `utils/datetime.py`: The Python file for your script.
* `utils/tests/test_datetime.py`: A basic test file.

Your `my-scripts` directory will look like this:

```console
my-scripts/
└── utils/
    ├── datetime.py
    └── tests/
        └── test_datetime.py
```

## Step 2: Inspect and Customize Your New Script

Open the generated `utils/datetime.py` file in your favorite text editor. It
will look something like this (we've slightly modified the default template for
this example):

```python
from tome.command import tome_command
from tome.api.output import TomeOutput # For standardized output
import datetime # We'll use the datetime module

@tome_command()
def dt(tome_api, parser, *args): # Changed name to 'dt' for brevity
    """
    Displays the current date and time, or a specific part.
    """
    parser.add_argument(
        '--format',
        type=str,
        help="Optional format string (e.g., '%Y-%m-%d', '%H:%M:%S')"
    )
    parser.add_argument(
        '--utc',
        action='store_true',
        help="Display time in UTC"
    )
    parsed_args = parser.parse_args(*args)

    now = datetime.datetime.utcnow() if parsed_args.utc else datetime.datetime.now()

    if parsed_args.format:
        output_str = now.strftime(parsed_args.format)
    else:
        output_str = now.isoformat()

    TomeOutput().info(output_str)
```

Key points:

* The function is named `dt` (so the command will be `utils:dt`).
* It uses the `datetime` module.
* It accepts an optional `--format` argument and a `--utc` flag.
* It uses `TomeOutput().info()` to print the result.

**Save the changes** to `utils/datetime.py` if you made any.

## Step 3: Install Your Local "Tome"

For **tome** to recognize and run scripts from your `my-scripts` directory, you
need to "install" this directory. We'll use an editable install (`-e`) so any
further changes to your scripts are picked up automatically.

From inside the `my-scripts` directory, run:

    $ tome install . -e

You should see a confirmation message.

## Step 4: Run Your New Command!

Now you can execute your `dt` script from anywhere using its full **tome** name
(`namespace:command_name`):

    $ tome utils:dt

This will output the current date and time in ISO format.

Let's try the options:

    $ tome utils:dt --utc

This shows the current time in UTC.

    $ tome utils:dt --format "%Y-%m-%d"

This shows only the current date.

    $ tome utils:dt --format "%H:%M:%S on %A" --utc

This shows the UTC time and the day of the week.

## Step 5: See Your Command Listed

You can always check what commands are available in a particular namespace:

    $ tome list utils

Output:

    ✨ utils commands
     utils:dt (e)  Displays the current date and time, or a specific part.

The `(e)` reminds you it's an editable installation.

## That's It!

You've successfully:

* Created a new namespaced command using `tome new`.
* Inspected and understood a basic **tome** Python script.
* Installed your local script collection in editable mode.
* Run your command with different arguments.
* Listed your command.

This is the basic workflow for managing your personal scripts with **tome**.

## Next Steps

* Explore Further: Check out the **[User Guides](../guides/index.md)** to learn
  about creating shell scripts, managing multiple "tomes" from different sources
  (like Git repositories), using subcommands, and more.
* Command Details: For a full list of **tome**'s own commands and their options,
  see the **[CLI Reference](../reference/cli.md)**.
