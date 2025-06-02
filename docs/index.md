# tome

<p class="tagline-highlight"><em>A set of tools to <strong>organize, share & run scripts</strong></em></p>

---

## What can tome do?

- 📂 **Organise** – [keep your scripts tidy and always
  accessible](overview/quickstart.md) with a clear folder structure.
- 🤝 **Share** – [distribute your script collections](guides/share.md) via Git,
  archives, or local folders.
- 🧪 **Test** – [test scripts](guides/testing.md) in one line to make sure they
  work as expected.
- 🔒 **Secure** – manage secrets with [tome vault](guides/features/vault.md).

---

## Install

Create and activate a **virtual environment**. For detailed instructions, refer
to the [install guide](overview/installing.md). Then, install **tome** using `pip`:

<div class="termy" data-termynal>
<span data-ty="input">pip install tomescripts</span>
<span data-ty>🎉  Tome installed.</span>
<span data-ty="input">tome --version</span>
<span data-ty>0.1.0</span>
</div>

---

## Hello world in 30 seconds

Use `tome new` to create a template for a command. Then **install** it in
editable mode. Now your changes are reloaded instantly. Afterwards, **list** all
available commands and **run it**.

```console
# create a new command
$ tome new greetings:hello

# install in editable mode
$ tome install . -e

# list installed commands
$ tome list

📖 ~/my-tome

  🌲 greetings commands
     greetings:hello (e)  Description of the command.

# run it!
$ tome greetings:hello Hello!
 ________
< Hello! >
 --------
        \\   @..@
         \\ (----)
           ( >__< )
           ^^ ~~ ^^
```

Install the examples from a third party, in this case the tome repository:

```console
# install tome examples from the github repository
$ tome install https://github.com/jfrog/tome.git --folder=examples

# list installed commands
$ tome list

📖 https://github.com/jfrog/tome.git

  🌐 network commands
     network:ping-bat               Script to ping an IP address or ...
     network:ping-sh                Script to ping an IP address or ...
     network:traceroute-bat         Script to perform a traceroute to ...
     network:traceroute-sh          Script to perform a traceroute to ...

  🖥️ system commands
     system:monitor                 Monitor system usage including CPU...

  📝 todo commands
     todo:tasks                     Manage your to-do list tasks.

# ask for help
$ tome system:monitor --help
usage: tome monitor [-h] [-v] [-q] [--cpu] [--memory] [--disk]

Monitor system usage including CPU, memory, and disk.

options:
  -h, --help     show this help message and exit
  -v, --verbose  Increase the level of verbosity (use -v, -vv, -vvv, etc.)
  -q, --quiet    Reduce the output to a minimum, showing only critical errors
  --cpu          Monitor CPU usage in real-time
  --memory       Monitor memory usage in real-time
  --disk         Display disk usage

# run the command
$ tome system:monitor --cpu --memory --disk
Disk Usage: 1.5% used
Total: 926.35 GB
Used: 10.47 GB
Free: 695.70 GB
CPU Usage: 19.1%
Memory Usage: 60.5%
Total: 36.00 GB
Used: 14.75 GB
Available: 14.24 GB
Free: 2.00 GB
```

---

## What's Next?

| Goal                               | Documentation                                                              |
| :--------------------------------- | :------------------------------------------------------------------------- |
| 🚀 **Get started in 5 minutes** | **[Quickstart](overview/quickstart.md)** |
| 📚 **Explore all CLI commands** | **[CLI Reference](reference/cli.md)** |
| ✨ **Contribute or get support** | **[Contribution Guide in GitHub](https://github.com/jfrog/tome/blob/main/CONTRIBUTING.md)** |
