# Sharing Your Tomes

Once you've created a **Tome** (your collection of scripts), you'll often want
to share it with others or use it across different machines. **tome**
facilitates this by allowing installation from various **Origins**.

## Key Methods for Sharing

### 1. Git Repositories
The most robust way to share and version your **Tomes** is by hosting them in a
Git repository (like GitHub, GitLab, or a private server).

- **How to share:** Commit your **Tome** directory structure (containing
  namespace folders and **Scripts**) to a Git repository.
- **How users install:**

```console
$ tome install https://github.com/your-user/your-tome-repo.git
```

They can also specify branches or tags:

```console
$ tome install https://github.com/your-user/your-tome-repo.git@my-feature-branch
```

### 2. Local Folders
For sharing within a team on a shared drive or for distributing scripts that are
part of a larger local project:

- **How to share:** Ensure the directory containing your **Tome** is accessible
  to others.
- **How users install:**

```console
$ tome install /path/to/shared/my-tome
```
Or, if they've copied it locally:
```console
$ tome install ./my-local-copy-of-tome
```

### 3. ZIP Archives (and other compressed files)
You can package your **Tome** into a ZIP file (or `.tar.gz`, etc.) for
distribution.

- **How to share:** Create a compressed archive of your **Tome** directory.
- **How users install:**
    - From a local file: `tome install /path/to/my-tome.zip`
    - From a URL: `tome install https://example.com/my-tome.zip`

## Using the `--folder` Option
If your actual scripts within a Git repository or ZIP file are located in a
subdirectory, users can point **tome** to it using the `--folder` flag during
installation:

```console
$ tome install <git_or_zip_source> --folder path/to/scripts_within_source
```

Choose the sharing method that best suits your workflow and distribution needs.
