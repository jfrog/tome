# 📖 Tome's basics

## 📝 Basic concepts

- **Tome**: group of commands
- **Origin**: `Tome` folder
- **Namespace**: `Tome` name
- **Command**: `@tome_command`
- **Script**: files inside a `Tome`
- **Vault**:
- **...**:

## 📚 tome commands

### Install a new command script

Install scripts from various sources. The source can be a git repository, local file or folder, zip file (local or http), or requirements file.

    tome install <source>                           # Install scripts from <source>
    tome install <source> -e                        # Install a <source> in editable mode.
    tome install <source> --no-ssl                  # Do not verify SSL connections.
    tome install <source> --create-env              # Create a new virtual environment, if the command depends on any requirements.
    tome install <source> --force-requirements      # If the origin contains a python requirements file, install those requirements even if not running tome in a virtual environment.
    tome install <source> --folder <folder>         # Specify a <folder<> within the source to install from.

### Create a new command

Create a new example recipe and source files from a template.

    tome new <namespace>:<command>      # Create a new example command named <command> insithe the folder <namespace>

### See my installed commands

List all the installed commands.

    tome list               # List all the commands
    tome list <pattern>     # List all the commands that match a given pattern.

### See a command information

Get information about a command.

    tome info <command_name>          # See all the info abut <command_name>

### tome configuration

Manage the tome configuration.

    tome config home         # print the current home folder
    tome config store        # print the current store folder

### tome test          

Run any test located by your script with pytest framework.

### tome uninstall

Uninstall scripts from various sources.

### tome vault      

Manage encrypted secret variables usable in any tome script.