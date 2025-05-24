import os
import textwrap

from tome.api.output import TomeOutput
from tome.command import tome_command
from tome.errors import TomeException
from tome.internal.api.new import default_tomeignore


def create_python_script(command_name, description):
    template = textwrap.dedent(f'''\
        """
        This is an example Tome command created using 'tome new'.

        For more information on Tome and how to create your own commands,
        please refer to the official documentation:
        https://jfrog.github.io/tome/
        """
        import os

        from tome.command import tome_command
        from tome.api.output import TomeOutput

        def frog_{command_name}(message):
            """
            Format the message in a speech bubble with a frog ASCII art.
            """
            lines = message.split('\\n')
            width = max(len(line) for line in lines)
            # build speech bubble
            top = ' ' + '_' * (width + 2)
            bottom = ' ' + '-' * (width + 2)
            bubble = [top]
            for line in lines:
                bubble.append(f"< {{line.ljust(width)}} >")
            bubble.append(bottom)
            frog = r"""
                \\\\   @..@
                 \\\\ (----)
                   ( >__< )
                   ^^ ~~ ^^
            """
            return "\\n".join(bubble) + frog


        @tome_command()
        def {command_name}(tome_api, parser, *args):
            """
            {description}
            """
            parser.add_argument('positional', help="Placeholder for a positional argument")
            parser.add_argument('-o', '--optional', help="Placeholder for an optional argument")
            args = parser.parse_args(*args)

            # Add your command implementation here
            tome_output = TomeOutput()
            msg = args.positional if args.optional is None else args.positional + ", " + args.optional
            tome_output.info(frog_{command_name}(msg))
        ''')

    return template


def create_shell_script(script_content, script_type, description):
    if not script_content:
        if script_type == "sh":
            script_content = textwrap.dedent(f'''\
                #!/bin/bash
                # tome_description: {description}
                #
                # This is an example Tome command created using 'tome new'.
                # For more info: https://jfrog.github.io/tome/

                echo 'Hello, world!'
            ''')
        elif script_type == "bat":
            script_content = textwrap.dedent(f'''\
                @echo off
                REM tome_description: {description}
                REM
                REM This is an example Tome command created using 'tome new'.
                REM For more info: https://jfrog.github.io/tome/

                echo Hello, world!
            ''')
    return script_content


def create_test(script_name, command_name):
    namespace = script_name.split(":")[0]

    return textwrap.dedent(f'''\
    from {namespace}.{command_name} import frog_{command_name}

    def test_frog_{command_name}_formatting():
        """
        Test the basic formatting of the frog_{command_name} function
        from {script_name.replace('_', '-')}.
        """
        message = "Test Message"
        output = frog_{command_name}(message)

        assert f"< {{message.ljust(len(message))}} >" in output
        assert " __" in output
        assert " --" in output
        assert r"        \\\\   @..@" in output
        assert r"         \\\\ (----)" in output
        assert r"           ( >__< )" in output
        assert r"           ^^ ~~ ^^" in output
    ''')


@tome_command()
def new(tome_api, parser, *args):  # noqa
    """
    Create a new example recipe and source files from a template.
    """
    parser.add_argument("script_name", help="Name for the script in a tome standard way, like namespace:script_name.")
    parser.add_argument(
        "--type", default="python", choices=["python", "sh", "bat"], help="Type of the script to create."
    )
    parser.add_argument("--script", help="Content of the script if type is 'sh' or 'bat'.")
    parser.add_argument("-f", "--force", action="store_true", help="Force overwrite of command if it already exists")
    parser.add_argument("--description", default="Description of the command.", help="Description of the command.")
    args = parser.parse_args(*args)

    tokens = args.script_name.split(":")
    if len(tokens) != 2:
        raise TomeException("Commands must be in the form namespace:command")
    out_folder = tokens[0]
    command_name = tokens[1].replace("-", "_")

    os.makedirs(out_folder, exist_ok=True)

    if args.type == "python":
        script_content = create_python_script(command_name, args.description)
    else:
        script_content = create_shell_script(args.script, args.type, args.description)

    extension = "py" if args.type == "python" else args.type

    if extension != "py":
        command_name = f"tome_{command_name}"

    script_path = os.path.join(out_folder, f"{command_name}.{extension}")

    if os.path.exists(script_path) and not args.force:
        raise TomeException(f"Command '{script_path}' already exist. Use -f/--force to overwrite")

    with open(script_path, 'w') as script_file:
        script_file.write(script_content)

    with open(".tomeignore", 'w') as tomeignore_file:
        tomeignore_file.write(default_tomeignore)

    if args.type == "python":
        tests_folder = os.path.join(out_folder, "tests")
        os.makedirs(tests_folder, exist_ok=True)
        with open(os.path.join(tests_folder, f"test_{command_name}.py"), 'w') as test_file:
            test_file.write(create_test(args.script_name, command_name))

    TomeOutput().info(f"Generated script: {script_path}")
    return {}
