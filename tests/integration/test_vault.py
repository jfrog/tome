import os
import textwrap
from tests.utils.tools import TestClient
from tome.internal.utils.files import mkdir


def test_vault_commands():
    client = TestClient()
    client.run("vault create -p potato")
    assert "Vault 'default' created" in client.out

    client.run("vault create -n foo -p bar")
    assert "Vault 'foo' created" in client.out

    client.run("vault add-secret token_1 'my key' --description 'my token token_1' -p potato")
    assert "Secret 'token_1' added to 'default' vault" in client.out

    client.run("vault add-secret token_2 'my key' -p potato")
    assert "Secret 'token_2' added to 'default' vault" in client.out

    client.run("vault add-secret token_3 'my key' --description 'my token token_3' -p potato")
    assert "Secret 'token_3' added to 'default' vault" in client.out

    client.run("vault add-secret token_4 'my key' --description 'my token token_4' -vn foo -p bar")
    assert "Secret 'token_4' added to 'foo' vault" in client.out

    client.run("vault delete -n foo -p potato", assert_error=True)
    assert "Error: Impossible to open vault 'foo'. Invalid password" in client.out

    client.run("vault list-secrets")
    assert "Vault 'default' secrets" in client.out
    assert "token_1       my token token_1" in client.out
    assert "token_2       No description" in client.out
    assert "token_3       my token token_3" in client.out
    assert "Vault 'foo' secrets" in client.out
    assert "token_4       my token token_4" in client.out

    client.run("vault delete-secret token_4 -vn foo -p bar")
    assert "Secret 'token_4' deleted from 'foo' vault" in client.out

    client.run("vault delete-secret token_3 -p potato")
    assert "Secret 'token_3' deleted from 'default' vault" in client.out

    client.run("vault list-secrets")
    assert "Vault 'default' secrets" in client.out
    assert "token_1       my token token_1" in client.out
    assert "token_2       No description" in client.out
    assert "token_3       my token token_3" not in client.out
    assert "Vault 'foo' secrets" not in client.out


def test_vault_command():
    client = TestClient()
    mkdir(os.path.join(client.current_folder, "greetings"))
    tome_script = textwrap.dedent(
        '''
        from tome.command import tome_command

        @tome_command()
        def read_text(tome_api, parser, *args):
            """read_text."""
            parser.add_argument('-p', '--password', help='Tome vault password')
            parser.add_argument('name', help="secret name")
            args = parser.parse_args(*args)
            my_vault = tome_api.vault.open(name='default', password=args.password)
            print(f"{my_vault.read(name=args.name)}")
    '''
    )
    client.save({os.path.join(client.current_folder, "greetings", "greetings-commands.py"): tome_script})

    client.run("install .")
    client.run("list")
    assert "greetings:read-text" in client.out
    client.run("vault create -p potato")
    client.run("vault add-secret token 'my key' -p potato")

    client.run("greetings:read-text token -p potato")
    assert "my key" in client.out

    client.run("greetings:read-text wrong_token -p potato")
    assert "None" in client.out

    client.run("greetings:read-text token -p wrong_potato", assert_error=True)
    assert "Error: Impossible to open vault 'default'. Invalid password" in client.out


def test_create_and_reuse_basic_secret_key():
    client = TestClient()
    mkdir(os.path.join(client.current_folder, "greetings"))

    tome_script = textwrap.dedent(
        '''
        from tome.command import tome_command
        import os

        @tome_command()
        def create(tome_api, parser, *args):
            """write."""
            parser.add_argument('-p', '--password', help='Tome vault password')
            parser.add_argument('name', help="secret name")
            parser.add_argument('text', help="secret text")
            args = parser.parse_args(*args)
            my_vault = tome_api.vault.open(name='default', password=args.password)
            status = my_vault.create(name=args.name, text=args.text)
            print(status)
            print(f"{my_vault.read(name=args.name)}")

        @tome_command()
        def read(tome_api, parser, *args):
            """read."""
            parser.add_argument('-p', '--password', help='Tome vault password')
            parser.add_argument('name', help="secret name")
            args = parser.parse_args(*args)
            my_vault = tome_api.vault.open(name='default', password=args.password)
            print(f"{my_vault.read(name=args.name)}")
    '''
    )
    client.save({os.path.join(client.current_folder, "greetings", "greetings-commands.py"): tome_script})

    client.run("install .")
    client.run("list")
    assert "greetings:create" in client.out
    assert "greetings:read" in client.out
    client.run("vault create -p potato")

    client.run("greetings:create token 'my token' -p potato")
    assert "Created" in client.out
    assert "my token" in client.out

    client.run("greetings:read token -p potato")
    assert "my token" in client.out

    client.run("greetings:read wrong_token -p potato")
    assert "None" in client.out

    client.run("greetings:read token -p wrong_potato", assert_error=True)
    assert "Error: Impossible to open vault 'default'. Invalid password" in client.out
