# Help & Support

If you need assistance while using **tome**, there are several ways to get help
directly from the command line. For other issues, feature requests, or if you're
interested in contributing, [our GitHub
repository](https://github.com/jfrog/tome) is the place to go.

## Using Built-in CLI Help

**tome** includes a helpful command-line interface to guide you.

### General Command Overview

To see a list of all available **tome** commands and their brief descriptions,
run:

```
$ tome --help
```

This will typically output something like:

```
📖 tome commands:
  config         Manage the tome configuration.
  info           Get information about a specific command.
  install        Install scripts from a source.
  list           List all the commands that match a given pattern.
  new            Create a new example recipe and source files from a template.
  test           Run any test located by your script with pytest framework.
  uninstall      Uninstall a tome of scripts.
  vault          Manage encrypted secret variables usable in any tome script.

Type 'tome <command> -h' for help
```

### Help for Specific Commands

If you need help with a particular command, its options, and arguments, you can
use the `--help` (or `-h`) flag after the command name.

For example, to get help for the `install` command:

```
$ tome install --help
```

This will show detailed usage information, similar to this:

```
usage: tome install [-h] [-v] [-q] [-f FORMAT] [-e] [--no-ssl] [--create-env] [--force-requirements] [--folder FOLDER] [source]

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

This detailed help is available for all **tome** commands and their subcommands.

### Checking The **tome** Version

To quickly check the installed version of **tome**, you can use the `--version`
flag:

```
$ tome --version
```

## Further Assistance

### Reporting Issues or Requesting Features

If you've found a bug, are facing a problem not covered in the documentation, or
have an idea for a new feature, please let us know by opening an issue on our
[GitHub repository](https://github.com/jfrog/tome/issues).

### Contributing to **tome**

We welcome contributions! If you're interested in helping improve **tome**,
please [check out our contributing guide](https://github.com/jfrog/tome/blob/main/CONTRIBUTING.md).
