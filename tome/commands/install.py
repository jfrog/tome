import json
from tome.api.output import TomeOutput
from tome.command import tome_command
from tome.errors import TomeException
from tome.internal.source import Source, SourceType


def print_install_text(source):
    output = TomeOutput(stdout=True)
    output.info(f"Installed source: {source.uri}")
    if source.commit:
        output.info(f"Commit: {source.commit}")


def print_install_json(source):
    output = TomeOutput(stdout=True)
    data = {
        "uri": source.uri,
        "type": str(source.type),
        "version": source.version,
        "commit": source.commit,
        "folder": source.folder,
    }
    output.print_json(json.dumps(data, indent=4))


@tome_command(formatters={"text": print_install_text, "json": print_install_json})
def install(tome_api, parser, *args):
    """
    Install scripts from a source.

    The source can be a git repository, a folder, or a zip file (local or http).
    Editable installations are supported with the -e/--editable flag.
    """
    parser.add_argument(
        "source",
        nargs="?",
        help="Source: a git repository, folder, or zip file (local or http).",
    )
    parser.add_argument("-e", "--editable", action="store_true", help="Install a package in editable mode.")
    parser.add_argument("--no-ssl", action="store_true", help="Do not verify SSL connections.")
    parser.add_argument(
        "--create-env",
        action="store_true",
        help="Create a new virtual environment if the command depends on any requirements.",
    )
    parser.add_argument(
        "--force-requirements",
        action="store_true",
        help="Install requirements even if not running tome in a virtual environment.",
    )
    parser.add_argument(
        "--folder", help="Specify a folder within the source to install from (only valid for git or zip file sources)."
    )
    args = parser.parse_args(*args)

    source = Source.parse(args.source)
    if args.folder:
        if source.type not in (SourceType.GIT, SourceType.FILE, SourceType.URL):
            raise TomeException("--folder argument is only compatible with git repositories and file sources.")
        source.folder = args.folder

    source.verify_ssl = not args.no_ssl

    if args.editable:
        source.type = SourceType.EDITABLE
        result = tome_api.install.install_editable(source, args.force_requirements, args.create_env)
    else:
        result = tome_api.install.install_from_source(source, args.force_requirements, args.create_env)

    return result
