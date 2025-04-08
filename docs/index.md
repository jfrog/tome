# > tome 📖

!!! Example "Tome index section. what is tome and a super simple example"
    - key features.
    - super simple example.

A powerful script management tool.

## Key Features

- Organize 📂: Effortlessly manage and structure your scripts for a clean, maintainable codebase.
- Collaborate 🤝: Seamlessly share and collaborate on scripts with your team to enhance productivity.
- Test 🧪: Ensure your scripts' reliability and performance with comprehensive testing tools.
- Secure 🔒: Manage and protect your passwords using the tome vaults.

Install `tome` using pip:

```bash
$ pip install tomescripts
```

We highly recommend to [install into a virtual environment](./introduction/installing_tome.md).

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

🚀 ci commands
 ci:check-pipeline-status       Check the status of a pipeline in the CI.
 ci:view-logs                   View build or deploy logs from the CI system.

☸️  k8s commands
 k8s:deploy                     Deploy a Kubernetes resource using a manifest.
 k8s:get-pods                   List all running pods in a Kubernetes cluster.

📡 server commands
 server:check-health            Perform a health check on a server.
 server:log-watch               Stream live logs from a server.
 server:restart                 Restart a specific server instance.
 server:scale-down              Decrease the number of server instances.
 server:scale-up                Increase the number of server instances.
```

## Running a Script

Execute a script invoking it with ``<namespace>:<command>`` like:

```bash
$ tome ci:check-pipeline-status --pipeline-id 427

🚀 Checking the status of pipeline #427...
Fetching pipeline details...
Pipeline ID: 427
Project: web-app-deployment
Status: Running
Started at: 2025-02-03 18:04:43 UTC
Duration: 11 minutes
📄 View pipeline details
📝 Latest commit: Fix login issue (commit hash: a1b2c3d4)
[2025-02-03 18:05:43.563673] - Cloning repository...
[2025-02-03 18:06:58.563673] - Running tests...
[2025-02-03 18:10:13.563673] - Building Docker image...
Pipeline still running...
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
