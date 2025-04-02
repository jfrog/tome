import getpass
import json
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


def print_vault_text(result):
    TomeOutput(stdout=True).print(result["message"])


def print_vault_json(result):
    result_to_print = result.copy()
    result_to_print.pop("message", None)
    TomeOutput(stdout=True).print_json(json.dumps(result_to_print, indent=4))


def print_list_secrets_text(result):
    output = TomeOutput(stdout=True)
    vaults = result.get("vaults", {})
    if not vaults:
        output.info("No secrets found.")
        return
    for vault_name, secrets_list in vaults.items():
        output.info(f"Vault '{vault_name}' secrets:")
        if secrets_list:
            max_name_length = max(len(item["secret"]) for item in secrets_list)
            padding_size = max_name_length + 6
            for item in secrets_list:
                secret_name = item["secret"].ljust(padding_size)
                description = item["description"]
                output.info(f"{secret_name} {description}")
        else:
            output.info("  No secrets found.")


@tome_command(parent=vault, formatters={"text": print_vault_text, "json": print_vault_json})
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
        if vault_password != vault_password_confirm:
            raise TomeException("The provided passwords do not match. Please try again.")
    tome_api.vault.create(name=args.name, password=vault_password)
    return {"message": f"Vault '{args.name}' created", "vault": args.name}


@tome_command(parent=vault, formatters={"text": print_vault_text, "json": print_vault_json})
def delete(tome_api, parser, *args):
    """Delete a vault"""
    parser.add_argument('-p', '--password', help='Tome vault password (Prompt if not specified)')
    parser.add_argument(
        '-n', '--name', help='Vault name (will use the "default" vault if not specified)', default='default'
    )
    args = parser.parse_args(*args)
    vault_password = _get_password(args.password)
    tome_api.vault.delete(name=args.name, password=vault_password)
    return {"message": f"Vault '{args.name}' deleted", "vault": args.name}


@tome_command(parent=vault, formatters={"text": print_vault_text, "json": print_vault_json})
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
    return {"message": f"Secret '{args.name}' added to '{args.vault}' vault", "vault": args.vault, "secret": args.name}


@tome_command(parent=vault, formatters={"text": print_vault_text, "json": print_vault_json})
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
    return {
        "message": f"Secret '{args.name}' deleted from '{args.vault}' vault",
        "vault": args.vault,
        "secret": args.name,
    }


@tome_command(parent=vault, formatters={"text": print_list_secrets_text, "json": print_vault_json})
def list_secrets(tome_api, parser, *args):
    """List available secrets id's and descriptions in all vaults"""
    args = parser.parse_args(*args)
    secrets = tome_api.vault.list()
    vaults_dict = {}
    for vault_name, secrets_info in secrets.items():
        if secrets_info:
            vaults_dict[vault_name] = [
                {"secret": name, "description": description or "No description"} for name, description in secrets_info
            ]
    return {"vaults": vaults_dict}
