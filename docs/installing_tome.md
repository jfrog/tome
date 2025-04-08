# Installing Tome

!!! Example "How to install tome"
    - pip install tomescript.
    - other installation options.

## pip package *(recommended)*

The recommended way to install **tome** is using `pip` within a virtual environment. This ensures that your project dependencies are isolated and managed effectively:

1. Create a virtual environment:

```
python -m venv myenv
```

2. Activate the virtual environment:

=== "UNIX/macOS"

    ```
    source myenv/bin/activate
    ```

=== "Windows"

    ```
    myenv\Scripts\activate
    ```

Install **tome** using `pip`:

```bash
pip install tomescripts
```

Now you can start using **tome**

## Other options

### install from source

1. Clone the tome git repository:

```
git clone https://github.com/jfrog/tome.git
```

2. Create a virtual environment:

```
python -m venv myenv
```

3. Activate the virtual environment:

=== "UNIX/macOS"

    ```
    source myenv/bin/activate
    ```

=== "Windows"

    ```
    myenv\Scripts\activate
    ```

4. Install **tome** using `pip`:

```bash
pip install -e <tome/git/repository/local/path>
```