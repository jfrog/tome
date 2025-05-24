# 📂 Store your secret variables

Tome vault allow you to store secret variable and reuse it in your commands.

!!! Example "📝 Basic concepts"

    - **Vault**: local secret store.
    - **Secret**: each string store inside a vault.
    - **Password**: vault password using to write, read and delete a vault secret. You can`t read/write your secret if you lost this password!.

## Manage your vaults

### Create a vault

```bash
tome vault create
Tome vault password:❓
Confirm tome vault password:❓
Vault 'default' created
```

```bash
tome vault create -p mypassword
Vault 'default' created
```

```bash
tome vault create -n myvault -p otherpassword
Vault 'myvault' created
```

### Manage your secrets

```bash
vault add-secret token_0 'my key'
Tome vault password:❓
Secret 'token_0' added to 'default' vault
```

```bash
vault add-secret token_1 'my key' --description 'my token token_1' -p mypassword
Secret 'token_1' added to 'default' vault
```

```bash
tome vault add-secret token_0 'other token 0' -vn myvault -p otherpassword
Tome vault password:❓
Secret 'token_0' added to 'myvault' vault
```

```bash
tome vault list-secrets
Vault 'default' secrets
token_1       my token token_1
token_0       No description
Vault 'myvault' secrets
token_0       No description
```

```bash
tome vault delete-secret token_0 -p mypassword
Secret 'token_0' deleted from 'default' vault
```

```bash
tome vault list-secrets
Vault 'default' secrets
token_1       my token token_1
Vault 'myvault' secrets
token_0       No description
```

### Delete a vault

```bash
tome vault delete
Tome vault password:❓
Vault 'default' deleted
```

```bash
tome vault delete -p mypassword
Vault 'default' deleted
```

```bash
tome vault delete -n myvault -p otherpassword
Vault 'myvault' deleted
```

## Using a secret inside your commands

First of all, we need to create a vault and a secret.

```bash
tome vault create -p mypassword
tome vault add-secret token 'my key' -p mypassword
```

Now, we can use this secret inside our python tome commands using the `tome_api.vault` API.

```python
from tome.command import tome_command

@tome_command()
def read_text(tome_api, parser, *args):
    """Read a secret."""
    parser.add_argument('-p', '--password', help='Tome vault password')
    parser.add_argument('name', help="secret name")
    args = parser.parse_args(*args)
    tome_output = TomeOutput()
    my_vault = tome_api.vault.open(name='default', password=args.password)
    tome_output.info(f"{my_vault.read(name=args.name)}")
```

Of course, we can create a secret inside our command using the same API.

```python
from tome.command import tome_command
import os

@tome_command()
def create(tome_api, parser, *args):
    """Create a secret."""
    parser.add_argument('-p', '--password', help='Tome vault password')
    parser.add_argument('name', help="secret name")
    parser.add_argument('text', help="secret text")
    args = parser.parse_args(*args)
    tome_output = TomeOutput()
    my_vault = tome_api.vault.open(name='default', password=args.password)
    status = my_vault.create(name=args.name, text=args.text)
    tome_output.info(status)
    tome_output.info(f"{my_vault.read(name=args.name)}")
```
