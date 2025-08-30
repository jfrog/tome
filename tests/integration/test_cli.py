import os
import textwrap
import shutil

from tests.utils.tools import TestClient


def test_multiple_command_levels():
    client = TestClient()

    tome_script = textwrap.dedent("""
        import os
        from tome.command import tome_command
        from tome.api.output import TomeOutput

        @tome_command()
        def level1(tome_api, parser, *args):
            '''
            Description of the level1.
            '''

        @tome_command(parent=level1)
        def level2(tome_api, parser, *args):
            '''
            Description of the level2.
            '''

        @tome_command(parent=level2)
        def level3(tome_api, parser, *args):
            '''
            Description of the level3.
            '''
            parser.add_argument('positional_argument', help="Placeholder for a positional argument")
            parser.add_argument('--optional-argument', help="Placeholder for an optional argument")
            args = parser.parse_args(*args)

            # Add your command implementation here
            tome_output = TomeOutput()
            tome_output.info(f"Tome command called with positional argument: {args.positional_argument}")
            if args.optional_argument:
               tome_output.info(f"Tome command called with optional argument: {args.optional_argument}")
    """)
    client.save({os.path.join(client.current_folder, "multiple", "multiple.py"): tome_script})
    client.run("install .")
    client.run("multiple:level1 --help")
    assert "usage: tome level1 [-h] [-v] [-q] {level2}" in client.out
    client.run("multiple:level1 level2 --help")
    assert "usage: tome level1 level2 [-h] [-v] [-q] {level3}" in client.out
    client.run("multiple:level1 level2 level3 --help")
    assert "usage: tome level1 level2 level3 [-h] [-v] [-q]" in client.out
    assert "positional_argument" in client.out
    assert "--optional-argument" in client.out
    client.run("multiple:level1 level2 level3 mypositionalargument --optional-argument myoptionalargument")
    assert "Tome command called with positional argument: mypositionalargument" in client.out
    assert "Tome command called with optional argument: myoptionalargument" in client.out


def test_sys_path():
    c = TestClient()

    tome_script = textwrap.dedent("""
        from myhelper import myprint
        from tome.command import tome_command

        @tome_command()
        def cmd(tome_api, parser, *args):
            '''
            Description
            '''
            myprint()
        """)
    helper_py = textwrap.dedent("""
        from tome.api.output import TomeOutput
        def myprint():
            TomeOutput(stdout=True).print("Hello {}!")
        """)

    c.save(
        {
            os.path.join(c.current_folder, "origin1", "cmds1", "mycmd.py"): tome_script,
            os.path.join(c.current_folder, "origin1", "cmds1", "myhelper.py"): helper_py.format("world"),
            os.path.join(c.current_folder, "origin2", "cmds2", "mycmd2.py"): tome_script,
            os.path.join(c.current_folder, "origin2", "cmds2", "myhelper.py"): helper_py.format("moon"),
        }
    )
    c.run("install origin1")
    c.run("cmds1:cmd")
    assert "Hello world!" in c.out
    c.run("install origin2")
    c.run("cmds2:cmd")
    assert "Hello moon!" in c.out
    c.run("cmds1:cmd")
    assert "Hello world!" in c.out


def test_missing_editable():
    """
    Test when a installed editable command is missing its folder later.
    """
    client = TestClient()
    os.mkdir(os.path.join(client.current_folder, "tome_commands"))

    client.run("new mynamespace:mycommand")
    shutil.move(
        os.path.join(client.current_folder, "mynamespace"),
        os.path.join(client.current_folder, "tome_commands", "mynamespace"),
    )
    client.run("install -e tome_commands")
    shutil.rmtree(os.path.join(client.current_folder, "tome_commands"))
    client.run("list")
    assert "No matches were found for '*' pattern." in client.out
