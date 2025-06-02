# Using Tome Vault for Secrets Management

Many scripts require access to sensitive information like API keys, database
passwords, or private tokens. Storing these directly in scripts is a security
risk. **tome**'s **Vault** feature provides a secure, local, and encrypted store
for this data, accessible only with a master password.

## Core Vault Concepts

* **Vault**: Your encrypted local datastore for secrets. You can have multiple
  named vaults (default is `default`).
* **Secret**: An individual piece of sensitive data (e.g., an API key) stored in
  a **Vault** under a specific name.
* **Password**: The master password for a **Vault**. **Remember it! Losing it
  means losing access to the secrets within.**

## Create a Script That Needs a Secret

Let's start by creating a new **tome** **Command**. Imagine we want a script
that fetches some data using an API, and this API requires an access token.

1.  Create a project directory and navigate into it:

```console
$ mkdir my-tome
$ cd my-tome
```

2.  Use `tome new` to create a script. We'll call it `getdata` in the
    `dataservice` namespace:

```console
$ tome new dataservice:getdata --description "Fetches data from some service."
Generated script: dataservice/getdata.py
```

3.  Now, let's edit `dataservice/getdata.py`. We'll make it *try* to access a
    secret named `api_token` from the `default` vault.

```python
# dataservice/getdata.py
from tome.command import tome_command
from tome.api.output import TomeOutput
from tome.errors import TomeException

@tome_command()
def getdata(tome_api, parser, *args):
    """
    Fetches data from some service.
    """
    parser.add_argument(
        '--vault-password',
        help="Password for the 'default' vault (will prompt if not provided)"
    )
    # In a real script, you might have other arguments like --endpoint, etc.
    parsed_args = parser.parse_args(*args)

    output = TomeOutput(stdout=True)
    error_output = TomeOutput() # For errors, to stderr

    # Attempt to open the 'default' vault
    default_vault = tome_api.vault.open(name='default', password=parsed_args.vault_password)

    api_token = default_vault.read(name='api_token')

    if api_token:
        output.info(f"Simulating API call...")
        # Here, you would use the api_token to make your actual API request
        output.info("Data fetched successfully!")
    else:
        error_output.warning("Could not retrieve 'api_token'. Is it set in the 'default' vault?")
```

**Important elements:**

* The script defines a `--vault-password` argument to potentially receive the
  vault password, though `tome_api.vault.open()` will prompt if it's not
  supplied and needed.
* It directly calls `tome_api.vault.open(name='default',
  password=parsed_args.vault_password)` to access the `default` vault. If the
  vault doesn't exist or the password (if prompted or provided) is incorrect,
  **tome** itself will typically raise an error.
* It then attempts to read a secret named `api_token` using
  `default_vault.read(name='api_token')`.
* Based on whether `api_token` is found, it prints a success simulation or a
  warning. Note that direct error handling for vault operations (like a wrong
  password for an existing vault) is not explicitly in this simplified script
  version; **tome** would handle such errors.

4.  Install this **Tome** as editable:

```console
$ tome install . -e
Configured editable installation for /path/to/my-tome
Installed source: /path/to/my-tome
```

## Step 2: First Attempt - The Expected Failure

If you try to run this command now, and you haven't set up any vaults or
secrets, it will likely fail or indicate that the secret is missing.

```console
$ tome dataservice:getdata --vault-password mydummy_pass_for_now
Error: Vault 'default' does not exist. Please run 'tome vault create' to create it first.
```

This is expected! Our script is trying to access a vault and a secret that don't
exist yet.

## Step 3: Setting Up the Vault and Secret

Now, let's use the `tome vault` CLI commands to create our `default` vault and
add the `api_token` secret.

1.  **Create the `default` vault:** You'll be prompted to set a new password for
    this vault. Choose a secure password and remember it.

```console
$ tome vault create
Tome vault password: mydummy_pass_for_now
Confirm tome vault password: mydummy_pass_for_now
Vault 'default' created
```

2.  **Add the `api_token` secret to the `default` vault:** You'll be prompted
    for the vault password you just set.

```console
$ tome vault add-secret api_token "SecretToken" --description "Access token"
Tome vault password: mydummy_pass_for_now
Secret 'api_token' added to 'default' vault.
```

    You can verify the secret name is listed (the value itself remains
    encrypted):

```console
$ tome vault list-secrets
Vault 'default' secrets:
api_token         Access token
```

## Step 4: Running the Script Successfully

Now that the `default` vault exists and contains the `api_token` secret, let's
run our `dataservice:getdata` command again. This time, provide the correct
vault password you set.

```console
$ tome dataservice:getdata --vault-password mydummy_pass_for_now
Simulating API call...
Data fetched successfully!
```

Success! Your script now securely accesses the API token from the **tome**
Vault.

## Step 5: Cleaning Up - Deleting the Secret

Once you are done with a secret, or if it was created for testing purposes, you
can remove it from the vault. To delete the `api_token` we created earlier from
the `default` vault, use the `tome vault delete-secret` command.

You will be prompted for the vault password:

```console
$ tome vault delete-secret api_token
Tome vault password: <enter_your_secure_password_here>
Secret 'api_token' deleted from 'default' vault.
```

You can confirm it's gone by listing the secrets again:

```console
$ tome vault list-secrets
No secrets found.
```

## Conclusion

In this guide, you've learned the essentials of **tome**'s Vault feature:

* How to write a Python **Command** that attempts to read a secret.
* The importance of creating a **Vault** and adding **Secrets** to it using
  `tome vault` CLI commands.
* How your script can successfully retrieve and use these stored secrets once
  the vault is set up.
* How to clean up by deleting secrets.
