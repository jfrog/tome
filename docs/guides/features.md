# Important Tome Features

Beyond basic script creation and execution, **tome** offers several key features
to streamline your script management. This page highlights some of the most
important ones. For full details, please refer to the [CLI Command
Reference](../reference/cli.md) and other specific guides.

## Namespaces & Origins
**Tome** uses **Namespaces** to logically group your **Commands** and prevent
naming conflicts, especially when you install multiple **Tomes**. Each **Tome**
is associated with an **Origin**, which is its source location (like a local
folder or a Git URL). This allows you to manage scripts from diverse sources
seamlessly.

## Python and Shell Script Support
**tome** isn't limited to one type of script. You can easily manage:

* **Python Scripts:** Define **Commands** using Python functions decorated with
  `@tome_command()`. Leverage `argparse` for argument handling and `TomeOutput`
  for standardized console messages.
* **Shell Scripts:** Integrate your existing `.sh`, `.bash`, `.bat`, or `.ps1`
  scripts. **tome** discovers them via a `tome_` prefix in the filename or by a
  shebang and a special `tome_description:` comment. (See [Migrate a
  Script](migrate_script.md)).

## Subcommands
For more complex tools, you can define **Commands** with multiple levels of
subcommands (e.g., `tome maincommand subcommand action`). This is achieved in
Python **Scripts** by specifying the `parent` argument in the `@tome_command()`
decorator.

## Editable Installs
When working on scripts locally, install your **Tome** using `tome install .
-e`. This "editable" mode means any changes you save to your script files are
immediately active when you run the **Command** via **tome**, without needing to
reinstall. This greatly speeds up development.

## Vault for Secrets
**tome** includes a secure vault to store sensitive information like API keys,
passwords, or tokens.

* **Manage:** Use `tome vault create`, `tome vault add-secret`, `tome vault
  list-secrets`, etc.
* **Access in Python Scripts:** Your Python **Commands** can securely access
  these secrets via the `tome_api.vault` object.
* *More details can be found in a dedicated [Vault Guide](./vault.md) (assuming
  you create this page).*

## Local Storage
If your **Commands** need a consistent place to read or write files (e.g., logs,
cache, data), **tome** provides a simple storage location accessible in Python
**Commands** via `tome_api.store.folder`. This points to a dedicated directory
within your **tome** home.
* *More details can be found in a dedicated [Local Storage
  Guide](./local_store.md) (assuming you create this page).*

## Dependency Management for Python Tomes
If a **Tome** containing Python **Scripts** has external package dependencies,
you can list them in a `requirements.txt` file at the root of the **Tome's
Origin**. The `tome install` command offers:

* `--create-env`: Creates an isolated virtual environment for the **Tome** and
  installs its dependencies there.
* `--force-requirements`: Installs dependencies into the current Python
  environment (use with an active virtual environment).
