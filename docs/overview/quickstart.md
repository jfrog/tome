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


    $ tome new utils:agecalc

This command will generate a couple of files:

* `utils/agecalc.py`: The Python file for your script containing the definition of the `utils:agecalc` command.
* `utils/tests/test_agecalc.py`: A basic test file.

Your `my-scripts` directory will look like this:

    my-scripts/
    └── utils/
        ├── agecalc.py
        └── tests/
            └── test_agecalc.py

## Step 2: Inspect and Customize Your New Script

Open the generated `utils/agecalc.py` file in your favorite text editor.
Let's modify the default template to implement our age calculator:

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

        output = TomeOutput()

        try:
            birth_date_obj = datetime.datetime.strptime(parsed_args.birthdate, '%Y-%m-%d').date()
        except ValueError:
            output.error("Invalid date format. Please use YYYY-MM-DD.")
            return

        today = datetime.date.today()

        age_years = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))

        output.info(f"You are {age_years} years old.")

Key points:

Explicar el decorador tome_command que sirve para definir agecalc como comando a correr... The function is named `agecalc` (so the command will be `utils:agecalc`).
el comando es agecalc  que toma de parametros la tome_api, parser y *args
Dentro del comando cogemos los argumentos de entrada con argparse, mencionar que esto no tiene nada de especial y que es uso standard de argparse con python
Mencionar el output con tomeouput que es la forma mas sencilla pero luego mas adelante quiero añadir formatters de json y text y explicarlos y decir por qué es buena idea usar formatters

* It uses the `datetime` module to parse the birthdate and calculate age.
* It accepts a `birthdate` argument.
* It uses `TomeOutput().info()` to print the result.

**Save the changes** to `utils/agecalc.py`.

## Step 3: Install Your Local "Tome"

For **tome** to recognize and run scripts from your `my-scripts` directory, you
need to "install" this **Tome** or directory of scripts. We'll use an editable
install (`-e`) so any further changes to your scripts are picked up
automatically.

From inside the `my-scripts` directory, run:

    $ tome install . -e

You should see a confirmation message.

## Step 4: Run Your New Command!

Now you can execute your `agecalc` script from anywhere using its full **tome** name
(`namespace:command_name`):

    $ tome utils:agecalc 1990-07-25

This will output the age in years. For example (output depends on the current date):

    You are 34 years old.

## Step 5: See Your Command Listed

You can always check what commands are available in a particular namespace:

    $ tome list utils

Output:

    ✨ utils commands
     utils:agecalc (e)  Calculates age based on a given birth date.

The `(e)` reminds you it's an editable installation.

## Next Steps

* Explore Further: Check out the **[User Guides](../guides/index.md)** to learn
  about creating shell scripts, managing multiple **Tomes** from different sources
  (like Git repositories), using subcommands, and more.
* Command Details: For a full list of **tome**'s own commands and their options,
  see the **[CLI Reference](../reference/cli.md)**.
