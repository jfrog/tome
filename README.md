# tome 📖

[![PyPI version](https://badge.fury.io/py/tomescripts.svg)](https://badge.fury.io/py/tomescripts)
[![CI Status](https://github.com/jfrog/tome/actions/workflows/main.yml/badge.svg)](https://github.com/jfrog/tome/actions/workflows/main.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**tome** is a powerful script management tool designed to streamline the
organization and distribution of scripts across different environments. Built
with flexibility and ease of use in mind, **tome** enhances how scripts of any
kind are managed, shared, tested, and maintained.

With **tome**, you can:

* **Organize** 📂: Effortlessly manage and structure your scripts for a clean,
  maintainable codebase. [Learn more in the Quickstart
  →](https://jfrog.github.io/tome/latest/overview/quickstart/)
* **Share & Collaborate** 🤝: Seamlessly distribute your script collections
  (Tomes) via Git, archives, or local folders. [See sharing options
  →](https://jfrog.github.io/tome/latest/guides/share/)
* **Test** 🧪: Ensure your scripts' reliability with integrated `pytest`
  support. [Read the testing guide
  →](https://jfrog.github.io/tome/latest/guides/testing/)
* **Secure** 🔒: Manage and protect sensitive data like API keys and passwords
  using the **tome** Vault. [Explore the Vault
  →](https://jfrog.github.io/tome/latest/guides/features/vault/)

---

## Installation

The recommended way to install **tome** is using `pip` within a virtual environment. This
ensures that your project dependencies are isolated and managed effectively:

1. Create a virtual environment:

```bash
python -m venv myenv
```

2. Activate the virtual environment:

On Windows:
```bash
myenv\Scripts\activate
```

On macOS/Linux:
```bash
source myenv/bin/activate
```

3. Install **tome** using `pip`:

```bash
pip install tomescripts
```

You're all set to start using **tome**!

---

## Quick Example: Hello Tome!

Get a feel for **tome** in under a minute:

```console
# 1. Create a new command template
$ tome new greetings:hello

# 2. Install your new Tome (in editable mode for development)
$ tome install . -e

# 3. Run your command!
$ tome greetings:hello "Hello"
 _______
< Hello >
 -------
        \\   @..@
         \\ (----)
           ( >__< )
           ^^ ~~ ^^
```

This simple example creates a Python script that prints a greeting with an ASCII
frog. With **tome**, this script is now an easily callable command.

---

## Documentation

For more detailed information on how to use **tome**, best practices, and guides, please
refer to our [official documentation](https://jfrog.github.io/tome/).

## Contribution

We welcome contributions to **tome**! Please read our contributing guidelines located in
[CONTRIBUTING.md](CONTRIBUTING.md) before submitting pull requests.

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) in this repository for details on our code of
conduct, which outlines our expectations for participants within the community.

## License

**tome** is released under the Apache License. See the bundled [LICENSE](LICENSE) file for
details.
