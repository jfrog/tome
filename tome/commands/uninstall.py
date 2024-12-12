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
        help="Source can be a git repository, local file or folder, " "zip file (local or http), or tomefile.yaml.",
    )
    parser.add_argument('-f', '--file', help="Uninstall from the given tomefile.yaml.")
    args = parser.parse_args(*args)

    if args.source and args.file:
        raise TomeException(
            "Cannot specify both a source and a tomefile.yaml. " "Please choose one uninstallation method."
        )

    if args.file:
        tome_api.install.uninstall_from_tomefile(args.file)
        return

    source = Source.parse(args.source)
    tome_api.install.uninstall_from_source(source)
