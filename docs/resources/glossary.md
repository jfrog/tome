# Glossary

Throughout this documentation, you will encounter several terms related to
**tome**. Here are definitions for some of the most important ones:

-   **Command** A runnable function defined within a **Script** file. In Python
    **Scripts**, these are typically functions decorated with `@tome_command()`.
    **Commands** belong to a **Tome** and are accessed via the **tome** tool
    using their **Namespace** and name (e.g., `tome namespace:command_name`).


-   **Namespace** The primary identifier used within the **tome** tool to group
    and access a collection of **Commands** originating from a specific
    **Tome**. It prevents naming conflicts, allowing, for example,
    `utils:cleanup` and `backup:cleanup` to coexist as distinct **Commands**.

-   **Origin** The source location from which the **Scripts** constituting a
    **Tome** are fetched or installed. Common examples include a Git repository,
    a local filesystem directory, or a ZIP archive.

-   **Script** A file (e.g., a Python `.py` file, or a shell script such as
    `.sh`, `.bat`) that contains the source code defining one or more
    **Commands**. **Scripts** are part of a **Tome**.

-   **Tome** A logical collection of **Scripts** that are sourced from a common
    **Origin**.

## Concepts in Action

Now, let's see how these terms apply in a practical scenario. We'll use `tome
new` to set up a small project.

Imagine you start in an empty directory:

- Create a project folder and navigate into it:

```console
$ mkdir my-tome
$ cd my-tome
```

- Generate two new commands using `tome new`, each in a different **namespace**

```console
$ tome new greetings:hello
$ tome new utils:showtime
```

- This action creates a directory structure similar to this:

```
my-tome/
├── greetings/
│   └── hello.py  (plus a tests/ directory)
└── utils/
    └── showtime.py (plus a tests/ directory)
```

- Install this **Tome** as editable.

```console
$ tome install . -e
```

Now, let's connect this setup to our glossary terms:

* The `my-tome/` directory serves as the **Origin** for your scripts, it's their
  source location.
* This collection of all scripts and files within `my-tome/` that **tome** now
  manages is a **Tome**.
* The subdirectories `greetings/` and `utils/` function as **Namespaces**,
  organizing your commands.
* Files like `greetings/hello.py` and `utils/showtime.py` are the **Scripts**
  where your command logic resides.
* The actual runnable tasks defined within these **Scripts** (e.g., the `hello`
  function in `hello.py`, exposed via `@tome_command`) become the **Commands**
  you can execute (like `tome greetings:hello`).
