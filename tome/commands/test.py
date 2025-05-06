import os
import sys
from tome.command import tome_command, CommandType
from tome.errors import TomeException


@tome_command()
def test(tome_api, parser, *args):
    """
    Run any test located by your script with pytest framework.
    """
    parser.add_argument(
        "pattern",
        help="Commands name pattern. Use '*' to launch all tests or 'namespace:command' to launch tests for a specific command.",
    )
    args = parser.parse_args(*args)

    commands = tome_api.list.filter_commands(args.pattern, [CommandType.cache, CommandType.editable])

    if not commands:
        raise TomeException(f"No commands found for pattern '{args.pattern}'.")

    python_paths = set()
    test_paths = set()
    test_commands = set()

    for command_info in commands:
        test_paths.add(os.path.join(command_info.base_folder, command_info.namespace))
        python_paths.add(command_info.base_folder)
        test_commands.add(command_info.name.replace("-", "_"))

    test_pattern = " or ".join(test_commands)

    old_sys_path = sys.path[:]
    try:
        import pytest

        sys.path.extend(python_paths)
        pytest_args = list(test_paths) + ["-k", test_pattern]

        if args.verbose:
            pytest_args.append("-v")

        pytest.main(pytest_args)
    except ImportError:
        raise TomeException("This command uses pytest as testing framework: 'pip install pytest'")
    finally:
        sys.path = old_sys_path
