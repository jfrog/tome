# CLI Command Reference

This page provides a reference for all built-in **Tome Commands** provided by
the **tome** tool.

For quick help from your terminal:
- General help and command list: `tome --help`
- Help for a specific command: `tome <command_name> --help`

---

## `tome config`
Manages **tome** configuration.

### `tome config home`
Prints the current **tome** home directory path. This is where **tome** stores
its cache, installed scripts, and other data. **Usage:** $ tome config home

### `tome config store`
Prints the path to **tome**'s local storage directory. Scripts can use this
location to persist data. **Usage:** $ tome config store

---

## `tome info`
Get detailed information about a specific installed **Command**.

**Usage:** $ tome info <namespace:command_name> [options]

**Arguments:**

* `namespace:command_name`: The full name of the command you want information
  about.

**Options:**

* `-f, --format <FORMAT>`: Specify output format (e.g., `json`).

---

## `tome install`
Installs a **Tome** (collection of scripts) from a specified **Origin**.

**Usage:** $ tome install [source] [options]

**Arguments:**

* `source` (optional): The **Origin** of the **Tome**. Can be:

    * A Git repository URL (e.g., `https://github.com/user/repo.git`). You can
      specify a branch/tag/commit with `@` (e.g., `repo.git@my-branch`).
    * A local directory path (e.g., `./my-scripts` or `/path/to/tome`). Defaults
      to `.` if not provided.
    * A URL or local path to a ZIP/tarball archive (e.g.,
      `http://example.com/scripts.zip`, `./archive.zip`).

**Options:**

* `-e, --editable`: Installs a local directory **Tome** in "editable" mode.
  Script changes are live without reinstalling.
* `--no-ssl`: Disables SSL certificate verification when downloading from HTTPS
  URLs.
* `--create-env`: If the **Tome** contains a `requirements.txt`, creates a
  dedicated Python virtual environment for it and installs dependencies there.
* `--force-requirements`: Installs dependencies from `requirements.txt` into the
  current Python environment. (Requires an active virtual environment if
  `--create-env` is not used).
* `--folder <FOLDER>`: For Git or archive **Origins**, specifies a subfolder
  within the source to install from.

---

## `tome list`
Lists all installed **Commands** that **tome** is aware of, optionally filtered
by a pattern.

**Usage:** $ tome list [pattern] [options]

**Arguments:**

* `pattern` (optional): A wildcard pattern to filter **Commands** by name or
  description. If omitted, lists all non-built-in commands.

**Options:**

* `-f, --format <FORMAT>`: Specify output format (e.g., `json`).

---

## `tome new`
Creates a new example **Script** and associated files (like tests) from a
template.

**Usage:** $ tome new <namespace:command_name> [options]

**Arguments:**

* `namespace:command_name`: The desired name for the new **Command**, including
  its **Namespace**.

**Options:**

* `--type <TYPE>`: Type of script to create. Choices: `python` (default), `sh`,
  `bat`.
* `--script <CONTENT>`: For `sh` or `bat` types, provide the initial content for
  the script.
* `-f, --force`: Overwrite if a script/command at the target path already
  exists.
* `--description "<DESCRIPTION>"`: A description for the new command (used in
  its docstring/help text).

---

## `tome test`
Runs tests for your installed **Tomes** using the `pytest` framework.

**Usage:** $ tome test <pattern>

**Arguments:**

* `pattern`: Specifies which tests to run.
    * `namespace:command_name`: Run tests for a specific command.
    * `namespace:*`: Run all tests for a given namespace.
    * `*`: Run all tests for all installed (non-built-in) **Tomes**.

---

## `tome uninstall`
Uninstalls a **Tome** from **tome**'s management.

**Usage:** $ tome uninstall <source_uri_or_path>

**Arguments:**

* `source_uri_or_path`: The **Origin** (Git URL, local path, archive path/URL)
  of the **Tome** you wish to uninstall. For editable installs, this is the
  local path that was installed.

---

## `tome vault`
Manages encrypted secret variables usable in your **tome** **Commands**. This
command has several subcommands. Run `tome vault --help` for a list.

*(You would then list and describe subcommands like `tome vault create`, `tome
vault add-secret`, `tome vault list-secrets`, `tome vault delete-secret`, `tome
vault delete`, similar to how they are in your `docs/tome_commands.md` and
`docs/features/vault.md`)*

---

*(Consider adding `tome --version` and `tome --help` as general tool options if
not covered adequately elsewhere, though `reference/cli.md` might be for
specific commands rather than global flags.)*
