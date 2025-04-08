# 📖 Tome's basics

## 📝 Basic concepts

- **Tome**: It is the collection of **scripts** that have a common **origin** (a folder, a git repository, ...).
- **Origin**: site where a **tome** comes from, it can be a git repository, a local folder or a zip file for example.
- **Namespace**: is the name of a **tome**, it is used to group **commands** and to be able to simply differentiate in a simple way two **commands** with the same name. For example `foo:hello` and `bar:hello`, in this case `foo` and `bar` would be two **namespaces** that both have a `hello` **command**.
- **Command**: `@tome_command`
- **Script**: All files inside a `Tome`
- **Vault**: Local secure storage space for all those variables used in a **tome** that you don't want to expose. An authentication token or an encryption key are an example of things you might want to store in a tome vault.

## 📚 tome commands

### Install a new command script

Install scripts from various sources. The source can be a git repository, local file or folder, zip file (local or http), or requirements file.

    tome install <source>                           # Install scripts from <source>
    tome install <source> -e                        # Install a <source> in editable mode.
    tome install <source> --no-ssl                  # Do not verify SSL connections.
    tome install <source> --create-env              # Create a new virtual environment, if the command depends on any requirements.
    tome install <source> --force-requirements      # If the origin contains a python requirements file, install those requirements even if not running tome in a virtual environment.
    tome install <source> --folder <folder>         # Specify a <folder> within the source to install from.

### Create a new command

Create a new example recipe and source files from a template.

    tome new <namespace>:<command>      # Create a new example command named <command> inside the folder <namespace>

### See my installed commands

List all the installed commands.

    tome list               # List all the commands
    tome list <pattern>     # List all the commands that match a given pattern.

### See a command information

Get information about a command.

    tome info <command_name>    # See all the info about <command_name>

### tome configuration

Manage the tome configuration.

    tome config home         # print the current home folder
    tome config store        # print the current store folder

### tome test          

Run any test located by your script with pytest framework.

    tome test <test_to_run>     # Use '*' to launch all tests or 'namespace:command' to launch tests for a specific command.

### tome uninstall

Uninstall scripts from various sources.

    tome uninsall <source>      # Source can be a git repository, local file or folder or zip file (local or http).

### tome vault      

Manage encrypted secret variables usable in any tome script.

    tome vault create -n <vault_name>                                                           # Create a new vault with a new password
    tome vault create -n <vault_name> -p <vault_password>                                       # Create a new vault with a new password without password prompt request
    tome vault delete -n <vault_name>                                                           # Delete a vault
    tome vault delete -n <vault_name> -p <vault_password>                                       # Delete a vault with a password without password prompt request
    tome vault add-secret <secret_name> <secret_text> -vn <vault_name> -p <vault_password>      # Add a new secret 
    tome vault add-secret <secret_name> <secret_text> -u                                        # Add a new secret or update if exists
    tome vault add-secret <secret_name> <secret_text> --descriptopn <secret_descriptopn>        # Add a new secret with a description
    tome vault delete-secret <secret_name> -vn <vault_name> -p <vault_password>                 # Delete a secret
    tome vault list-secrets                                                                     # List available secrets id's and descriptions in all vaults