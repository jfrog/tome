from tome.command import tome_command
from tome.errors import TomeException
from tome.internal.source import Source


@tome_command()
def uninstall(tome_api, parser, *args):
    """
    Uninstall scripts from various sources.
    """
    parser.add_argument(
        "source",
        nargs='?',
        help="Source can be a git repository, local file or folder, or zip file (local or http).",
    )
    args = parser.parse_args(*args)

    source = Source.parse(args.source)
    tome_api.install.uninstall_from_source(source)
