# Testing Your Scripts

Writing tests for your **tome** **Commands** is crucial for ensuring they behave
as expected and for maintaining them over time. **tome** leverages `pytest` for
its testing capabilities.

## Tests Structure

Let's see an example. When you create a new Python-based **Command** using `tome
new namespace:commandname`, **tome** automatically generates a basic test file
for you, typically at `namespace/tests/test_commandname.py`.

This provides a starting point for your tests. For example, if `tome new
greet:hello` created `greet/hello.py` and a helper function
`frog_hello`, your test file might look like:

<guide the user here with tome new and show tests folder structure>

```python
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

*(Adjust the import and function based on what your `tome new` template actually
generates for tests).*

## Writing Tests

You can write any standard `pytest` tests. Focus on:

- Testing helper functions within your **Scripts**.
- Testing the core logic of your **Command** functions. For complex commands,
  you might mock the `tome_api` and `parser` arguments or test the function that
  your **Command** calls after parsing arguments.

## Running Tests with `tome test`

The `tome test` **Tome Command** is used to discover and run your `pytest` tests
for installed **Tomes**.

1.  **Test a Specific Command:** If you want to run tests associated with a
    particular command:
    ```console
    $ tome test yournamespace:yourcommand
    ```

2.  **Test All Commands in a Namespace:**
    ```console
    $ tome test yournamespace:*
    ```

3.  **Test All Commands in All Installed Tomes:** (This applies to Tomes
    installed from cache or in editable mode)
    ```console
    $ tome test "*"
    ```

**tome** will look for test files (typically `test_*.py` or `*_test.py`) within
the directories of the **Tomes** that match your pattern and execute them using
`pytest`.

**Prerequisites for Testing:**

* Make sure `pytest` is installed in your Python environment:
  ```console
  $ pip install pytest
  ```
* Your **Tome** (the one containing the scripts and tests) must be installed via
  `tome install` (either normally or with `-e`).
