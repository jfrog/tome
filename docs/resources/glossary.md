# Glossary

When you run a **tome command** like `tome new`, a new collection of scripts
(which we call a "Tome") is typically initialized in your local directory. This
process usually creates a **Script** file, which in turn defines a runnable
**Command**.

Let's imagine we execute the following in the directory
`/users/johndoe/tome-example`:

    $ tome new greetings:hello

This action sets up a few things. Let's identify the key elements created or
involved:

    /users/johndoe/tome-example  -> Origin: This local directory is the source of our new collection.
      │                             The collection of scripts and associated files here forms a Tome.
      │
      └── greetings/                -> Namespace: A way to group and uniquely identify commands.
          ├── hello.py            -> Script: The file where the 'hello' Command is defined.
          │                             (Inside, a function like `def hello(...)` decorated with
          │                              `@tome_command` becomes the actual Command.)
          └── tests/
              └── test_hello.py   -> Tests for the 'hello' Command.

Now, let's formally define these identified elements:

-   **Tome Command** A built-in command provided by the **tome** tool itself,
    used for managing **Tomes** and the tool's general operation. In our
    example, `tome new` is a **Tome Command**. Other examples include `tome
    install` and `tome list`.

-   **Origin** The source location from which the **Scripts** constituting a
    **Tome** are fetched or installed. In our example, the **Origin** is the
    local directory `/users/johndoe/tome-example`. Other common **Origins**
    include Git repositories or ZIP archives.

-   **Tome** A logical collection of **Scripts** that are sourced from a common
    **Origin** (like our `tome-example` directory) and are typically organized
    under one or more **Namespaces** within the **tome** tool.

-   **Namespace** The primary identifier used within **tome** to group a set of
    related **Commands** from a specific **Tome**. In the example, `greetings`
    is the **Namespace**. It helps prevent naming conflicts, allowing, for
    instance, `greetings:hello` and `utils:hello` to exist as distinct
    **Commands**.

-   **Script** A file that contains the source code defining one or more
    **Commands**. In our example, `greetings/hello.py` is the **Script**. This
    could be a Python `.py` file, a shell script (`.sh`, `.bat`), etc.

-   **Command** An executable function or an entire script file that performs a
    specific task. In our example, the `hello` function (decorated with
    `@tome_command`) inside `hello.py` becomes the `hello` **Command** within
    the `greetings` **Namespace**. Users run **Commands** via **tome** like so:
    `tome greetings:hello`. This is distinct from a **Tome Command**.
