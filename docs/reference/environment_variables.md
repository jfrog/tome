# Environment Variables

**tome**'s behavior can be influenced by environment variables. Setting these
before running **tome** allows for customization.

## `TOME_HOME`

* **Purpose:** Specifies a custom absolute path for the **tome** home directory.
    This is where **tome** stores its operational data, including cached
    scripts, local storage, and vaults.

* **Default Value:** If not set, **tome** uses a `.tome` directory in your user
    home (e.g., `~/.tome` on Linux/macOS).

* **Example Usage (Linux/macOS):**

```console
$ export TOME_HOME="/path/to/my/custom_tome_home"
$ tome list
# tome will now use the custom path
```

You can check the active home directory with `tome config home`.

```console
$ tome config home
/path/to/my/custom_tome_home
```
