# > tome 📖

A powerful script management tool.

!!! Example "Key Features"

    - 📂 Organize: Effortlessly manage and structure your scripts for a clean, maintainable codebase.
    - 🤝 Collaborate: Seamlessly share and collaborate on scripts with your team to enhance productivity.
    - 🧪 Test: Ensure your scripts' reliability and performance with comprehensive testing tools.
    - 🔒 Secure: Manage and protect your passwords using the tome vaults.

Install `tome` using pip:

```bash
$ pip install tomescripts
```

We highly recommend to [install into a virtual environment](installing_tome.md#pip-package-recommended).

## Installing scripts

You can install scripts from various sources like a git repository, local file or folder,
zip file (local or http), or requirements file.

For example, you can install the examples from the **tome** repository by doing:

```bash
$ tome install https://github.com/jfrog/tome.git --folder=examples
```

!!! info

    Use the ``--folder`` argument when you have your scripts under a subfolder instead the root of the repository


## Listing Available Scripts

To list all installed scripts:

```bash
$ tome list
Results for '*' pattern:

🌐 network commands
 network:ping            Script to ping an IP address or URL. Arguments: <IP or URL>.
 network:traceroute      Script to perform a traceroute to an IP address or URL. Arguments: <IP or URL>.

🖥️  system commands
 system:monitor          Monitor system usage including CPU, memory, and disk.

📝 todo commands
 todo:tasks              Manage your to-do list tasks.
```

## Running a Script

Execute a script invoking it with ``<namespace>:<command>`` like:

```bash
$ tome system:monitor --cpu 
CPU Usage: 3.6%
```

## Creating a New Script

Create a new script with a predefined structure as a starting point using:

```bash
$ tome new <namespace>:<command>
```

Example:

```bash
$ tome new greetings:hello
```

To start using it, you can install this tome command as editable so that you can see the
changes while you are developing.

```bash
$ tome install . -e
```

The command will appear marked as editable: ``(e)`` if you do a ``tome list``:

```bash
$ tome list

...
🌲 greetings commands
 greetings:hello (e)            Description of the command.
...

```

You can open the ``./greetings/hello.py`` file with the editor of your choice and start
making changes. The changes will be inmediately applied when you are doing them because we
have installed it as `editable`.

!!! info
    For more details on the tome commands syntax inside ``hello.py`` please check [using tome section](./using_tome.md#edit-your-command).

## Testing Scripts

Tome supports testing using the ``tome test`` command. If you check the files that tome
new created you will see a tests folder with a ``test_hello.py`` file inside. To run those
tests just run:

```bash
$ tome test greetings:hello
```

To run tests over all installed commands:

```bash
$ tome test "*"
```

!!! info
    ``tome test`` command uses [pytest](https://docs.pytest.org/en/stable/) under the hood, please install it by doing ``pip install pytest``.
    For more information about testing your scripts with tome please check the [using tome section](./using_tome.md#test-your-command-namespace).
