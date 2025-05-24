# Frequently Asked Questions

Here are answers to some common questions about using **tome**.

### What's the main difference between a "Tome" and a "Namespace"?

A **Tome** is the actual collection of **Script** files that come from a
specific **Origin** (like a project folder or a Git repository). A **Namespace**
is the label or prefix you use *within* **tome** to call the **Commands** from
that **Tome**. For example, you might install a **Tome** from
`/projects/my-utils`, and its **Commands** could be under the `utils`
**Namespace** (e.g., `tome utils:my-util-command`). One **Tome** can even
contain multiple **Namespaces** if its directory structure is organized that
way.

### Can I use scripts written in languages other than Python?

Yes! **tome** is designed to run Python scripts (where commands are typically
functions decorated with `@tome_command()`) as well as general shell scripts.
For shell scripts (like `.sh`, `.bash`, `.bat`, `.ps1`), **tome** can discover
them if their filenames start with `tome_` or if they have a shebang and include
a `tome_description:` comment. See the [Migrate a
Script](../guides/migrate_script.md) guide for more details.

### How do I update a **Tome** that I installed from a Git repository?

To update a **Tome** installed from Git to the latest version of its default
branch, you can simply run `tome install <repository_url>` again. **tome** will
fetch the latest changes. If you installed a specific branch or tag (e.g., `tome
install <repository_url>@mybranch`), you'll need to re-run the install command
with that same branch/tag reference to get its latest commit.

### My Python scripts have dependencies. How does **tome** handle them?

If your Python-based **Tome** requires specific packages, you can include a
`requirements.txt` file in the root directory of your **Tome's Origin**. When
users install your **Tome**, they can use:
- `tome install <source> --create-env`: This tells **tome** to create a
  dedicated virtual environment for that **Tome** and install the dependencies
  from `requirements.txt` into it. The path to this environment is then
  associated with the **Commands** from that **Tome**.
- `tome install <source> --force-requirements`: This will install the
  dependencies into the user's currently active Python environment. (It's
  generally recommended to be in a virtual environment when using this).

### What's "editable" install (`tome install -e .`)?

When you install a local directory as a **Tome** using the `-e` or `--editable`
flag, **tome** creates a link to your scripts rather than copying them. This
means any changes you make to your local script files are immediately reflected
when you run the corresponding **Command** through **tome**, without needing to
run `tome install` again. It's very useful for development.

---
Still have questions? Check out [Help & Support](../overview/help.md) or [open
an issue](https://github.com/jfrog/tome/issues).
