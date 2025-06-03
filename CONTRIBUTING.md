# How to Contribute

## Setup

If you wish to contribute or modify **tome**, follow these steps to clone the repository
and install it in editable mode with all the required development dependencies. It is
recommended to **create a virtual environment** to ensure that your project dependencies
are isolated.

```
git clone https://github.com/jfrog/tome.git
cd tome
pip install -e .
```

Install the development dependencies:

```
pip install ".[dev]"
```

We use [pre-commit](https://pre-commit.com/) to enforce code style and formatting. To
activate the pre-commit hooks:

```
pre-commit install
```

This will ensure that every time you commit changes, the code will be formatted and linted
according to the project's standards.

If you want to run the checks manually, you can use the following command:

```
pre-commit run --all-files
```

## Running the Tests

It is mandatory to **use a virtual environment** to ensure that all tests will be able to
run without any restriction. Otherwise, some tests may fail.

**tome** uses `pytest` for its test suite. Ensure you have `pytest` installed:

```
pip install ".[dev]"
```

To run the tests, execute the following command from the project root directory:

```
pytest
```

## Building the Documentation

**tome**'s documentation is managed with [MkDocs](https://www.mkdocs.org/). To build the
documentation locally, first install the dependencies:

```
pip install ".[docs]"
```

Once installed, you can build the documentation site using the following command from the
project root directory:

```
mkdocs build
```

This will build the static site and place it in the `site/` directory by default. To serve
the documentation locally and view it in your browser, run:

```
mkdocs serve
```

## Style Guide

To keep the codebase consistent and easy to read, **tome** follows [PEP
8](https://www.python.org/dev/peps/pep-0008/) and [Black code
style](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html).
