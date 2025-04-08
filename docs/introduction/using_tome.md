# Using Tome

## Prerequisites

- Python 3.9
- tome installed

## Create and install your first basic command

```
mkdir tome-introduction
cd tome-introduction
tome new intro:hello
tome install . -e
```

## Test your command namespace

```sh
tome test intro
```

## Edit your command

```py
import os

from tome.command import tome_command
from tome.api.output import TomeOutput

def format_message_hello(message):
    """
    Add exclamations for a message
    """
    return message + "!!!"


@tome_command()
def hello(tome_api, parser, *args):
    """
    Description of the command.
    """
    parser.add_argument('positional_argument', help="Placeholder for a positional argument")
    parser.add_argument('--optional-argument', help="Placeholder for an optional argument")
    args = parser.parse_args(*args)

    # Add your command implementation here
    tome_output = TomeOutput()
    tome_output.info(format_message_hello(f"Tome command called with positional argument: {args.positional_argument}"))
    if args.optional_argument:
       tome_output.info(format_message_hello(f"Tome command called with optional argument: {args.optional_argument}"))
```

## Use the tome store API to write and read files locally

```py
from tome.command import tome_command
from tome.api.output import TomeOutput


@tome_command()
def write(tome_api, parser, *args):
    '''Write a file with tome.'''
    with open(tome_api.store.folder + '/asset.txt', 'w') as file:
        file.write('Hello world from file!\n')


@tome_command()
def read(tome_api, parser, *args):
    '''Read a file with tome.'''
    with open(tome_api.store.folder + '/asset.txt', 'r') as file:
        TomeOutput().info(file.read())
```

## Use a tome vault to store your secret variables

```sh
tome vault create -n intro -p my_password
tome vault add-secret hello_text 'my secret hello world' --description 'my secret hello text' -vn intro -p my_password
tome vault list-secrets
```

```py
@tome_command()
def read_secret(tome_api, parser, *args):
    """Read a secret with tome."""
    parser.add_argument('-p', '--password', help='Tome vault password')
    parser.add_argument('name', help="secret name")
    args = parser.parse_args(*args)
    my_vault = tome_api.vault.open(name='default', password=args.password)
    print(f"{my_vault.read(name=args.name)}")
```

## Uninstall your command

```sh
tome uninstall .
```

## Store remotelly your command and install from git