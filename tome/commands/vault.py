import getpass
from tome.command import tome_command
from tome.errors import TomeException
from tome.api.output import TomeOutput


def _get_password(vault_password):
    if not vault_password:
        vault_password = getpass.getpass('Tome vault password: ')
    return vault_password


@tome_command()
def vault(tome_api, parser, *args):
    """
    Manage encrypted secret variables usable in any tome script.
    """


@tome_command(parent=vault)
def create(tome_api, parser, *args):
    """Create a new vault with a new password"""
    parser.add_argument('-p', '--password', help='Tome vault password (Prompt if not specified)')
    parser.add_argument(
        '-n', '--name', help='Vault name (will use the "default" vault if not specified)', default='default'
    )
    args = parser.parse_args(*args)
    vault_password = args.password
    if not vault_password:
        vault_password = getpass.getpass('Tome vault password: ')
        vault_password_confirm = getpass.getpass('Confirm tome vault password: ')
        if not vault_password == vault_password_confirm:
            raise TomeException('Invalid password')
    tome_api.vault.create(name=args.name, password=vault_password)
    TomeOutput().info(f"Vault '{args.name}' created")


@tome_command(parent=vault)
def delete(tome_api, parser, *args):
    """Delete a vault"""
    parser.add_argument('-p', '--password', help='Tome vault password (Prompt if not specified)')
    parser.add_argument(
        '-n', '--name', help='Vault name (will use the "default" vault if not specified)', default='default'
    )
    args = parser.parse_args(*args)
    vault_password = _get_password(args.password)
    tome_api.vault.delete(name=args.name, password=vault_password)
    TomeOutput().info(f"Vault '{args.name}' deleted")


@tome_command(parent=vault)
def add_secret(tome_api, parser, *args):
    """Add a new secret"""
    parser.add_argument('-p', '--password', help='Tome vault password (Prompt if not specified)')
    parser.add_argument('-u', '--update', action='store_true', help='Update if exists')
    parser.add_argument('--description', help="Secret text description")
    parser.add_argument(
        '-vn', '--vault', help='Vault name (will use the "default" vault if not specified)', default='default'
    )
    parser.add_argument('name', help="Secret text name")
    parser.add_argument('text', help="Secret text content")
    args = parser.parse_args(*args)
    vault_password = _get_password(args.password)
    myvault = tome_api.vault.open(name=args.vault, password=vault_password)
    myvault.create(args.name, args.text, args.description, args.update)
    TomeOutput().info(f"Secret '{args.name}' added to '{args.vault}' vault")


@tome_command(parent=vault)
def delete_secret(tome_api, parser, *args):
    """Delete a secret"""
    parser.add_argument('-p', '--password', help='Tome vault password (Prompt if not specified)')
    parser.add_argument(
        '-vn', '--vault', help='Vault name (will use the "default" vault if not specified)', default='default'
    )
    parser.add_argument('name', help="Secret text name")
    args = parser.parse_args(*args)
    vault_password = _get_password(args.password)
    myvault = tome_api.vault.open(name=args.vault, password=vault_password)
    myvault.delete(args.name)
    TomeOutput().info(f"Secret '{args.name}' deleted from '{args.vault}' vault")


@tome_command(parent=vault)
def list_secrets(tome_api, parser, *args):
    """List available secrets id's and descriptions in all vaults"""
    args = parser.parse_args(*args)
    secrets = tome_api.vault.list()
    if secrets:
        for vault_name, secrets_info in secrets.items():
            if secrets_info:
                TomeOutput().info(f"Vault '{vault_name}' secrets")
                max_name_length = max(len(name) for name, _ in secrets_info)
                padding_size = max_name_length + 6
                for name, description in secrets_info:
                    padded_name = name.ljust(padding_size)
                    TomeOutput().info(f'{padded_name} {description or "No description"}')
