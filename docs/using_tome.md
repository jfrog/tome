# 📖 Using tome

!!! Example "basic concepts and complete example"
    - basic terminology explanation.
    - complete example about how to use tome and create a basic command.

## 📝 Basic concepts

- **Tome command**: All the tome builin commands like `tome install`, `tome list`, etc.
- **Tome**: It is the collection of **Scripts** that have a common **Origin** (a folder, a git repository, ...).
- **Origin**: site where a **Tome** comes from, it can be a git repository, a local folder or a zip file for example.
- **Namespace**: is the name of a **Tome**, it is used to group **Commands** and to be able to simply differentiate in a simple way two **Commands** with the same name. For example `foo:hello` and `bar:hello`, in this case `foo` and `bar` would be two **Namespaces** that both have a `hello` **Command**.
- **Command**: All the commands defined inside a **Tome** under a **Namespace**.
- **Script**: All files inside a **Tome** where the **Commnads** are defined.

## Using Tome

### Prerequisites

- Python 3.9
- (tome installed)[installing_tome.md]

### Create and install your first basic command

```bash
mkdir tome-introduction
cd tome-introduction
tome new intro:hello
```

This command will create something simillar to this file structure:

```bash
.
└── intro
    ├── hello.py
    └── tests
        └── test_hello.py
```

```bash
tome install . -e
```

### Test your command namespace

```bash
tome test intro
```

### Edit your command

If you open `intro/hello.py`, you will see the following script.

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

Any python tome command has some common elements:
- Use [argparse](https://docs.python.org/3/library/argparse.html) as cli parameter parser.
- You need to defane a `@tome_command()` decorator in any commnad.
    - If you want to create a subcommand, you need to define the previous command in the decorator.
- Is recommended to use the `TomeOutput()` to write any message.

Lets try to add a new command and a subcommand.

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
def say(tome_api, parser, *args):
    """
    Say something.
    """

@tome_command(parent=say)
def hello(tome_api, parser, *args):
    """
    Hello commnad.
    """
    parser.add_argument('user', help="hello user")
    args = parser.parse_args(*args)
    tome_output = TomeOutput()
    tome_output.info(format_message_hello(f"Hello {args.user}!"))


@tome_command(parent=say)
def bye(tome_api, parser, *args):
    """
    Bye command.
    """
    parser.add_argument('--optional-argument', help="optional bye user")
    args = parser.parse_args(*args)
    tome_output = TomeOutput()
    bye_user = args.optional_argument or "everyone"
    tome_output.info(format_message_hello(f"Bye {bye_user}!"))
```

!!! note
    If you want to migrate your own scripts, visit the [How to migrate a script to tome](how-to/script_to_tome.md) tutorial.

### Uninstall your command

```bash
tome uninstall .
```
