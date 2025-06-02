# Testing Your Scripts

Writing tests for your **tome** **Commands** is crucial for ensuring they behave
as expected and for maintaining them over time. **tome** leverages `pytest` for
its testing capabilities.

**Prerequisites for Testing:**

* Make sure `pytest` is installed in your Python virtual environment:

```console
$ pip install pytest
```

* Your **Tome** (the one containing the **Scripts** and their corresponding
  `tests` directories) must be installed via `tome install` (either normally or
  with the `-e` flag for editable installs).

## Initial Test Setup

When you create a new Python-based **Command** using `tome new
<namespace>:<commandname>`, **tome** automatically generates not only the script
file but also a corresponding test file.

Let's see an example. Suppose you run:

```console
$ mkdir my-tome
$ cd my-tome
$ tome new greet:hello --description "A friendly greeting command."
Generated script: greet/hello.py
```

This will create the following directory structure within `my-tome/`:

```text
my-tome/
└── greet/
    ├── hello.py           # Your command script
    └── tests/             # Directory for tests
        └── test_hello.py  # Basic test file for hello.py
```

As you can see, a `tests` subdirectory is created within your `greet`
**Namespace** folder, containing `test_hello.py`.

The generated `greet/hello.py` (based on your project's template) might include
a helper function, for instance, `frog_hello` for formatting the output with an
ASCII frog. The corresponding `greet/tests/test_hello.py` would then have a
basic test for that helper:

```python
# greet/tests/test_hello.py
from greet.hello import frog_hello

def test_frog_hello_formatting():
    """
    Test the basic formatting of the frog_hello function
    from greet:hello.
    """
    message = "Test Message"
    output = frog_hello(message)

    assert f"< {message.ljust(len(message))} >" in output
    assert " __" in output
    assert " --" in output
    assert r"        \\   @..@" in output
    assert r"         \\ (----)" in output
    assert r"           ( >__< )" in output
    assert r"           ^^ ~~ ^^" in output
```

* **Note:** The content of `test_hello.py` above, especially the
`frog_hello` import and the assertions, are based on the "ASCII frog" example
from your `tome new` template seen in `docs/index.md` and
`tome/commands/new.py`. Ensure this example test aligns with the actual test
file your `tome new` command currently generates. If it generates a different
helper or test, update this example accordingly.

## Running Tests with `tome test`

The `tome test` **Tome Command** is your primary tool for running tests. It
discovers and executes `pytest` tests for your installed **Tomes**.

*   **Test a Specific Command:** If you want to run tests associated with a
    particular **Command** (e.g., tests in `greet/tests/test_hello.py` for the
    `greet:hello` command):

    ```console
    $ tome install . -e  # Ensure your Tome is installed
    $ tome test greet:hello
    ```

*   **Test All Commands in a Namespace:** To run all tests for **Commands**
    within the `greet` **Namespace**:

    ```console
    $ tome test greet:*
    ```

*   **Test All Commands in All Installed Tomes:** (This applies to **Tomes**
    installed from the cache or in editable mode)

    ```console
    $ tome test "*"
    ```
