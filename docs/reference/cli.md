# Command-Line Interface (CLI) Reference

This page provides a comprehensive reference for all built-in **Tome Commands**.

For quick help from your terminal, you can always use:

* General help and list of commands: `tome --help`
* Help for a specific command: `tome <command_name> --help`
* Help for a subcommand: `tome <command_name> <subcommand_name> --help`

Global options available for most commands:

* `-v, --verbose`: Increase the level of verbosity (can be used multiple times,
  e.g., `-vv`, `-vvv`).
* `-q, --quiet`: Reduce the output to a minimum, showing only critical errors.

---

## `tome` (General Usage)

Running `tome` without any arguments or with just `--help` provides a list of
all top-level available commands.

```console
$ tome --help

📖 tome commands:
  config         Manage the tome configuration.
  info           Get information about a specific command.
  install        Install scripts from a source.
  list           List all the commands that match a given pattern.
  new            Create a new example recipe and source files from a template.
  test           Run any test located by your script with pytest framework.
  uninstall      Uninstall a tome of scripts.
  vault          Manage encrypted secret variables usable in any tome script.
```

---

## `tome config`

Manages **tome** configuration settings, such as the home directory and storage
path. This command has subcommands to query specific configuration values.

**Usage:**

```console
$ tome config --help

usage: tome config [-h] [-v] [-q] {home,store} ...

Manage the tome configuration.

positional arguments:
  {home,store}    sub-command help
    home          print the current home folder
    store         print the current store folder

options:
  -h, --help      show this help message and exit
  -v, --verbose   Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet     Reduce the output to a minimum, showing only critical errors
```

### `tome config home`

Prints the absolute path to the current **tome** home directory. This is the
root directory where **tome** stores its cache, installed scripts, vaults, and
other operational data.

**Usage:**

```console
$ tome config home --help

usage: tome config home [-h] [-v] [-q]

options:
  -h, --help      show this help message and exit
  -v, --verbose   Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet     Reduce the output to a minimum, showing only critical errors
```

### `tome config store`

Prints the absolute path to **tome**'s local storage directory. Scripts managed
by **tome** can use this location to persist their own data, like configuration
files or caches.

**Usage:**

```console
$ tome config store --help

usage: tome config store [-h] [-v] [-q]

options:
  -h, --help      show this help message and exit
  -v, --verbose   Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet     Reduce the output to a minimum, showing only critical errors
```

---

## `tome info`

Retrieves and displays detailed information about a specific installed
**Command**.

**Usage:**

```console
$ tome info --help

usage: tome info [-h] [-v] [-q] [-f FORMAT] command_name

Get information about a specific command.

positional arguments:
  command_name          The full name of the command (e.g., namespace:command).

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet           Reduce the output to a minimum, showing only critical errors
  -f FORMAT, --format FORMAT
                        Select the output format: json
```

---

## `tome install`

Installs a **Tome** (collection of scripts) from a specified **Origin**, making
its **Commands** discoverable and executable by **tome**.

**Usage:**

```console
$ tome install --help

usage: tome install [-h] [-v] [-q] [-f FORMAT] [-e] [--no-ssl] [--create-env]
                      [--force-requirements] [--folder FOLDER]
                      [source]

Install scripts from a source.

    The source can be a git repository, a folder, or a zip file (local or http).
    Editable installations are supported with the -e/--editable flag.

positional arguments:
  source                Source: a git repository, folder, or zip file (local or http).

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet           Reduce the output to a minimum, showing only critical errors
  -f FORMAT, --format FORMAT
                        Select the output format: json
  -e, --editable        Install a package in editable mode.
  --no-ssl              Do not verify SSL connections.
  --create-env          Create a new virtual environment if the command depends on any requirements.
  --force-requirements  Install requirements even if not running tome in a virtual environment.
  --folder FOLDER       Specify a folder within the source to install from (only valid for git or zip file sources).
```

---

## `tome list`

Lists all installed **Commands** that **tome** is aware of, optionally filtered
by a pattern.

**Usage:**

```console
$ tome list --help

usage: tome list [-h] [-v] [-q] [-f FORMAT] [pattern]

List all the commands that match a given pattern.

positional arguments:
  pattern               Commands name pattern. By default, it shows all the commands

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet           Reduce the output to a minimum, showing only critical errors
  -f FORMAT, --format FORMAT
                        Select the output format: json
```

---

## `tome new`

Creates a new example **Script** (and associated test files for Python scripts)
from a template, placing it within the specified **Namespace**.

**Usage:**

```console
$ tome new --help

usage: tome new [-h] [-v] [-q] [--type {python,sh,bat}] [--script SCRIPT] [-f]
                  [--description DESCRIPTION]
                  script_name

Create a new example recipe and source files from a template.

positional arguments:
  script_name           Name for the script in a tome standard way, like namespace:script_name.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet           Reduce the output to a minimum, showing only critical errors
  --type {python,sh,bat}
                        Type of the script to create.
  --script SCRIPT       Content of the script if type is 'sh' or 'bat'.
  -f, --force           Force overwrite of command if it already exists
  --description DESCRIPTION
                        Description of the command.
```

---

## `tome test`

Runs tests for your installed **Tomes** using the `pytest` framework. **tome**
will look for test files (typically `test_*.py` or `*_test.py`) within the
directories of the **Tomes** that match your pattern.

**Usage:**

```console
$ tome test --help

usage: tome test [-h] [-v] [-q] pattern

Run any test located by your script with pytest framework.

positional arguments:
  pattern               Commands name pattern. Use '*' to launch all tests or 'namespace:command' to launch tests for a specific command.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet           Reduce the output to a minimum, showing only critical errors
```

---

## `tome uninstall`

Uninstalls a **Tome** from **tome**'s management, based on its **Origin**.

**Usage:**

```console
$ tome uninstall --help

usage: tome uninstall [-h] [-v] [-q] [-f FORMAT] [source]

Uninstall a tome of scripts.

positional arguments:
  source                Source: a git repository, folder, or zip file (local or http).

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet           Reduce the output to a minimum, showing only critical errors
  -f FORMAT, --format FORMAT
                        Select the output format: json
```

---

## `tome vault`

Manages encrypted secret variables that can be used by your **tome**
**Commands**. This command has several subcommands for creating vaults,
adding/removing secrets, and listing secrets.

**Usage:**

```console
$ tome vault --help

usage: tome vault [-h] [-v] [-q]
                  {create,delete,add-secret,delete-secret,list-secrets} ...

Manage encrypted secret variables usable in any tome script.

positional arguments:
  {create,delete,add-secret,delete-secret,list-secrets}
                        sub-command help
    create              Create a new vault with a new password
    delete              Delete a vault
    add-secret          Add a new secret
    delete-secret       Delete a secret
    list-secrets        List available secrets id's and descriptions in all vaults

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet           Reduce the output to a minimum, showing only critical errors
```

### `tome vault create`

Creates a new encrypted vault. You will be prompted for a password to secure it.

**Usage:**

```console
$ tome vault create --help

usage: tome vault create [-h] [-v] [-q] [-f FORMAT] [-p PASSWORD] [-n NAME]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet           Reduce the output to a minimum, showing only critical errors
  -f FORMAT, --format FORMAT
                        Select the output format: json
  -p PASSWORD, --password PASSWORD
                        Tome vault password (Prompt if not specified)
  -n NAME, --name NAME  Vault name (will use the "default" vault if not specified)
```

### `tome vault delete`

Deletes an existing vault and all secrets within it. This action is
irreversible.

**Usage:**

```console
$ tome vault delete --help

usage: tome vault delete [-h] [-v] [-q] [-f FORMAT] [-p PASSWORD] [-n NAME]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet           Reduce the output to a minimum, showing only critical errors
  -f FORMAT, --format FORMAT
                        Select the output format: json
  -p PASSWORD, --password PASSWORD
                        Tome vault password (Prompt if not specified)
  -n NAME, --name NAME  Vault name (will use the "default" vault if not specified)
```

### `tome vault add-secret`

Adds a new secret (a key-value pair) to a specified vault.

**Usage:**

```console
$ tome vault add-secret --help

usage: tome vault add-secret [-h] [-v] [-q] [-f FORMAT] [-p PASSWORD] [-u]
                              [--description DESCRIPTION] [-vn VAULT]
                              name text

positional arguments:
  name                  Secret text name
  text                  Secret text content

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet           Reduce the output to a minimum, showing only critical errors
  -f FORMAT, --format FORMAT
                        Select the output format: json
  -p PASSWORD, --password PASSWORD
                        Tome vault password (Prompt if not specified)
  -u, --update          Update if exists
  --description DESCRIPTION
                        Secret text description
  -vn VAULT, --vault VAULT
                        Vault name (will use the "default" vault if not specified)
```

### `tome vault delete-secret`

Removes a specific secret from a vault.

**Usage:**

```console
$ tome vault delete-secret --help

usage: tome vault delete-secret [-h] [-v] [-q] [-f FORMAT] [-p PASSWORD]
                                [-vn VAULT]
                                name

positional arguments:
  name                  Secret text name

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet           Reduce the output to a minimum, showing only critical errors
  -f FORMAT, --format FORMAT
                        Select the output format: json
  -p PASSWORD, --password PASSWORD
                        Tome vault password (Prompt if not specified)
  -vn VAULT, --vault VAULT
                        Vault name (will use the "default" vault if not specified)
```

### `tome vault list-secrets`

Lists the names and descriptions of all secrets stored in all vaults. The secret
values themselves are not displayed.

**Usage:**

```console
$ tome vault list-secrets --help

usage: tome vault list-secrets [-h] [-v] [-q] [-f FORMAT]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet           Reduce the output to a minimum, showing only critical errors
  -f FORMAT, --format FORMAT
                        Select the output format: json
```
