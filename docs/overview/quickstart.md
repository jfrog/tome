# Quickstart: Your First 5 Minutes with Tome

This guide will get you from zero to running your own custom script in about 5
minutes. We'll create a simple script, install it with **tome** as editable so we
can make live changes to it and run it.

Throughout this guide, you will encounter several terms specific to **tome**.
For detailed definitions, we invite you to review our
[Glossary](../resources/glossary.md).

## Step 1: Initialize Your Script Collection (Your "Tome")

First, let's create a dedicated directory for our scripts. This directory will
represent your personal **Tome** or collection of scripts.

    $ mkdir my-scripts
    $ cd my-scripts

Next, we'll use **tome** to scaffold a new script. We'll create a script named
`agecalc.py` in the `utils` **namespace**. This script will define the
`utils:agecalc` **command**, which calculates your age based on your birth date.

```console
$ tome new utils:agecalc
```

This command will generate a couple of files:

* `utils/agecalc.py`: The Python file for your script containing the definition of the `utils:agecalc` command.
* `utils/tests/test_agecalc.py`: A basic test file.

Your `my-scripts` directory will look like this:

```console
my-scripts/
└── utils/
    ├── agecalc.py
    └── tests/
        └── test_agecalc.py
```

## Step 2: Inspect and Customize Your New Script

Open the generated `utils/agecalc.py` file in your favorite text editor. Let's
modify the default template to implement our age calculator. Initially, it will
print directly, but we'll change this later to use formatters.

```python
from tome.command import tome_command
from tome.api.output import TomeOutput
import datetime

@tome_command()
def agecalc(tome_api, parser, *args):
    """
    Calculates age based on a given birth date.
    """
    parser.add_argument(
        'birthdate',
        type=str,
        help="Your birth date in YYYY-MM-DD format (e.g., '1990-07-25')"
    )
    parsed_args = parser.parse_args(*args)

    output = TomeOutput() # For now, we'll use it for errors and direct output

    try:
        birth_date_obj = datetime.datetime.strptime(parsed_args.birthdate, '%Y-%m-%d').date()
    except ValueError:
        output.error("Invalid date format. Please use YYYY-MM-DD.")
        return # Exit if date is invalid

    today = datetime.date.today()
    age_years = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))

    # Initial direct output
    output.info(f"You are {age_years} years old.")
    # We will modify this function later to return data for formatters
```

**Key points about this script structure:**

* **`@tome_command()` Decorator**: The `@tome_command()` decorator above the `agecalc` function is essential. It registers `agecalc` with **tome** so it can be run as a command. For more details on its options (like defining subcommands or `formatters`), see the [**tome_command Decorator Reference**](../reference/python_api.md#tome_command-decorator). * **Command Function Signature**: The `agecalc` function, like all **tome** Python commands, takes `tome_api`, `parser`, and `*args` as parameters. You can learn more about these in the [Command Function Signature Reference](../reference/python_api.md#command-function-signature). * `tome_api`: Provides access to **tome**'s features (not used in this simple version).
    * `parser`: An `argparse.ArgumentParser` instance provided by **tome** for defining command-line arguments.
    * `*args`: The arguments passed to your command.
* **Argument Parsing**: We use `parser.add_argument(...)`. This is standard Python `argparse` functionality.
* **Output with `TomeOutput`**: For now, `TomeOutput().info()` prints directly. Later, we'll explore more flexible output using formatters.

**Save the changes** to `utils/agecalc.py`.

## Step 3: Install Your Local "Tome"

For **tome** to recognize and run scripts from your `my-scripts` directory, you
need to "install" this **Tome**. We'll use an editable install (`-e`) so any
further changes to your scripts are picked up automatically.

From inside the `my-scripts` directory, run:

```console
$ tome install . -e
```

You should see a confirmation message.

## Step 4: Run Your New Command!

Now you can execute your `agecalc` script:

```console
$ tome utils:agecalc 1990-07-25
```

This will output the age in years. For example (output depends on the current date):

```console
You are 34 years old.
```

## Step 5: See Your Command Listed

Check what commands are available:

```console
$ tome list utils

📖 ~/my-scripts

  🐮 utils commands
     utils:agecalc (e)  Calculates age based on a given birth date.
```

The `(e)` reminds you it's an editable installation.

## Step 6: Enhancing Output with Formatters

Instead of printing directly, **tome** **Commands** can return data and use
**formatters** to control the presentation (e.g., plain text or JSON). This is
particularly useful for structured output. You can learn more about how to
define and use them in the [Output Formatters
Reference](../reference/python_api.md#output-formatters). Let's modify
`utils/agecalc.py` to use this pattern:

1.  **Update the `agecalc` function to return data and define formatters:**

        from tome.command import tome_command
        from tome.api.output import TomeOutput
        import datetime
        import json # Required for JSON formatting

        # Formatter functions
        def age_text_formatter(data_dict):
            output = TomeOutput(stdout=True)
            if "error" in data_dict:
                output.error(data_dict["error"])
            else:
                output.info(f"Based on birthdate {data_dict.get('birthdate_input', 'N/A')}, calculated age is {data_dict.get('calculated_age_years', 'N/A')} years.")

        def age_json_formatter(data_dict):
            output = TomeOutput(stdout=True)
            output.print_json(json.dumps(data_dict, indent=4))

        @tome_command(formatters={"text": age_text_formatter, "json": age_json_formatter})
        def agecalc(tome_api, parser, *args):
            """
            Calculates age based on a given birth date.
            Supports --format text (default) or --format json.
            """
            parser.add_argument(
                'birthdate',
                type=str,
                help="Your birth date in YYYY-MM-DD format (e.g., '1990-07-25')"
            )
            parsed_args = parser.parse_args(*args)

            try:
                birth_date_obj = datetime.datetime.strptime(parsed_args.birthdate, '%Y-%m-%d').date()
            except ValueError:
                return {"error": "Invalid date format. Please use YYYY-MM-DD."}

            today = datetime.date.today()
            age_years = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))

            return {"birthdate_input": parsed_args.birthdate, "calculated_age_years": age_years, "status": "success"}

2.  **Save the `utils/agecalc.py` file.**

**Key changes for formatters:**
- The `agecalc` function now `return`s a dictionary.
- We defined `age_text_formatter` and `age_json_formatter`.
- The `@tome_command()` decorator was updated with a `formatters` argument.

Now, **tome** automatically adds a `--format` option to your command.

Try it out:

Default text output:
    $ tome utils:agecalc 1990-07-25

Output:
    Based on birthdate 1990-07-25, calculated age is 34 years.

JSON output:
    $ tome utils:agecalc 1990-07-25 --format json

Output:
    {
        "birthdate_input": "1990-07-25",
        "calculated_age_years": 34,
        "status": "success"
    }

## That's It!

You've successfully:

* Created a new namespaced command using `tome new`.
* Implemented a Python script that returns data.
* Defined and used output formatters for text and JSON.
* Installed your local script collection in editable mode.
* Run your command with different arguments and output formats.
* Listed your command.

This showcases how **tome** handles script creation, execution, and flexible output formatting.

## Next Steps

* Explore Further: Check out the **[User Guides](../guides/index.md)** to learn
  about creating shell scripts, managing multiple **Tomes** from different sources
  (like Git repositories), subcommands, and more advanced formatter usage.
* Command Details: For a full list of **tome**'s own commands and their options,
  see the **[CLI Reference](../reference/cli.md)**.
