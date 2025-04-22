# 📚 Tome commands

## Install a new command script

Install scripts from various sources. The source can be a git repository, local file or folder, zip file (local or http), or requirements file.

```bash
tome install <source>                           # Install scripts from <source>
tome install <source> -e                        # Install a <source> in editable mode.
tome install <source> --no-ssl                  # Do not verify SSL connections.
tome install <source> --create-env              # Create a new virtual environment, if the command depends on any requirements.
tome install <source> --force-requirements      # If the origin contains a python requirements file, install those requirements even if not running tome in a virtual environment.
tome install <source> --folder <folder>         # Specify a <folder> within the source to install from.
```

## Create a new command

Create a new example recipe and source files from a template.

```bash
tome new <namespace>:<command>      # Create a new example command named <command> inside the folder <namespace>
```

## See my installed commands

List all the installed commands.

```bash
tome list               # List all the commands
tome list <pattern>     # List all the commands that match a given pattern.
```

## See a command information

Get information about a command.

```bash
tome info <command_name>    # See all the info about <command_name>
```

## tome configuration

Manage the tome configuration.

```bash
tome config home         # print the current home folder
tome config store        # print the current store folder
```

## tome test          

Run any test located by your script with pytest framework.

```bash
tome test <test_to_run>     # Use '*' to launch all tests or 'namespace:command' to launch tests for a specific command.
```

## tome uninstall

Uninstall scripts from various sources.

```bash
tome uninstall <source>      # Source can be a git repository, local file or folder or zip file (local or http).
```

## tome vault      

Manage encrypted secret variables usable in any tome script.

```bash
tome vault create -n <vault_name>                                                           # Create a new vault with a new password
tome vault create -n <vault_name> -p <vault_password>                                       # Create a new vault with a new password without password prompt request
tome vault delete -n <vault_name>                                                           # Delete a vault
tome vault delete -n <vault_name> -p <vault_password>                                       # Delete a vault with a password without password prompt request
tome vault add-secret <secret_name> <secret_text> -vn <vault_name> -p <vault_password>      # Add a new secret 
tome vault add-secret <secret_name> <secret_text> -u                                        # Add a new secret or update if exists
tome vault add-secret <secret_name> <secret_text> --description <secret_description>        # Add a new secret with a description
tome vault delete-secret <secret_name> -vn <vault_name> -p <vault_password>                 # Delete a secret
tome vault list-secrets                                                                     # List available secrets id's and descriptions in all vaults
```