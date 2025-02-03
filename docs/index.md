# > tome

An efficient tool to manage scripts with ease.

## Highlights

- 🚀 Manage and execute scripts effortlessly.
- ⚡️ Install scripts from local folders, Git repositories, or archives.
- 🔒 Securely store and retrieve secrets using the built-in vault.
- 🛠️ Debug and test scripts effectively.
- 📁 Organize and share scripts efficiently.

## Getting Started

Install `tome` using pip:

```bash
pip install tome
```

You can also install from source:

```bash
git clone https://github.com/jfrog/tome.git
cd tome
pip install .
```

## Using Tome Scripts

### Listing Available Scripts

To list all installed scripts:

```bash
tome list
```

### Running a Script

Execute a script using:

```bash
tome <namespace>:<command> [arguments]
```

Example:

```bash
tome greetings:hello "Hello, world!"
```

## Creating and Managing Scripts

### Creating a New Script

Generate a new script with:

```bash
tome new <namespace>:<command>
```

Example:

```bash
tome new greetings:hello
```

### Installing Scripts

To install scripts from a directory:

```bash
tome install <source-folder>
```

Example:

```bash
tome install .
```

To install from a Git repository:

```bash
tome install https://github.com/user/repo.git
```

### Uninstalling Scripts

To remove a script:

```bash
tome uninstall <namespace>:<command>
```

Or uninstall all scripts from a source:

```bash
tome uninstall <source-folder>
```

## Vault System for Secure Storage

Tome includes a vault for securely storing secrets.

### Creating a Vault

```bash
tome vault create -p mypassword
```

### Adding Secrets

```bash
tome vault add-secret my_token "secret_value" -p mypassword
```

### Listing Secrets

```bash
tome vault list-secrets -p mypassword
```

### Retrieving a Secret

```bash
tome vault get-secret my_token -p mypassword
```

### Deleting a Secret

```bash
tome vault delete-secret my_token -p mypassword
```

## Debugging Scripts

For debugging purposes, use:

```bash
tome <namespace>:<command> --debug
```

## Testing Scripts

Tome supports testing with:

```bash
tome test <namespace>:<command>
```

To run all tests:

```bash
tome test *
```

## Configuration

To check the Tome home directory:

```bash
tome config home
```

To set a custom home directory:

```bash
export TOME_HOME=/custom/path
```

## Contributions

Contributions are welcome! Fork the repository, make changes, and submit a pull request.

## License

Tome is licensed under the Apache License 2.0. See the LICENSE file for details.

For more details, visit the [official documentation](https://jfrog.github.io/tome/).
