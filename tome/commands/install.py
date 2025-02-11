from tome.api.output import TomeOutput
from tome.command import tome_command
from tome.errors import TomeException
from tome.internal.source import Source, SourceType


@tome_command()
def install(tome_api, parser, *args):
    """
    Install scripts from various sources.
    """
    parser.add_argument(
        "source",
        nargs='?',
        help="Source can be a git repository, local file or folder, zip file (local or http), or requirements file.",
    )
    parser.add_argument('-e', '--editable', action='store_true', help="Install a package in editable mode.")
    parser.add_argument('-f', '--file', help="Install from the given tomefile.yaml.")
    parser.add_argument('--no-ssl', action='store_true', help='Do not verify SSL connections.')
    parser.add_argument(
        '--create-env',
        action='store_true',
        help='Create a new virtual environment, if the command depends on any requirements.',
    )
    parser.add_argument(
        '--force-requirements',
        action='store_true',
        help='If the origin contains a python requirements file, '
        'install those requirements even if not running tome in a virtual environment.',
    )
    parser.add_argument(
        '--folder', help='Specify a folder within the source to install from. Only valid for git or file sources.'
    )
    args = parser.parse_args(*args)

    if args.source and args.file:
        raise TomeException("Cannot specify both a source and a tomefile.yaml. Please choose one installation method.")

    # check using source similar to: https://pip.pypa.io/en/latest/topics/vcs-support/
    if args.file:
        summary = tome_api.install.install_from_tomefile(args.file, args.force_requirements, args.create_env)
        _show_tome_file_status(summary)
        return

    source = Source.parse(args.source)

    # Allow --folder only for sources of type GIT or FILE.
    # this does not make sense for local folders because you can already specify the folder in the source
    if args.folder:
        if source.type not in (SourceType.GIT, SourceType.FILE, SourceType.URL):
            raise TomeException("--folder argument is only compatible with git repositories and file sources.")
        source.folder = args.folder

    source.verify_ssl = not args.no_ssl
    if args.editable:
        source.type = SourceType.EDITABLE
        tome_api.install.install_editable(source, args.force_requirements, args.create_env)
    else:
        tome_api.install.install_from_source(source, args.force_requirements, args.create_env)


# FIXME: make this more consistent with the rest of the output
#  make all install API methods return the same information
#  and output through a formatter instead using this method
def _show_tome_file_status(summary):
    output = TomeOutput()
    skipped = summary.get('skipped', {})
    installed = summary.get('installed', {})
    failed = summary.get('failed', {})
    output.info('\n')
    for source, status in installed.items():
        status = f' ({status})' if status else ''
        output.info(f'  [ INSTALLED ] {source}{status}')
    for source, status in skipped.items():
        output.info(f'  [ SKIPPED ] {source}')
        for line in status.split('\n'):
            output.info(f'      {line}')
    for source, status in failed.items():
        output.info(f'  [ FAILED ] {source}')
        for line in status.split('\n'):
            output.info(f'      {line}')
