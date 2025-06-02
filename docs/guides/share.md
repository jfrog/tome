# Sharing Your Tomes

Once you've created a **Tome** (your collection of scripts), you'll likely want
to share it with your team, other users, or simply use it across different
machines. **tome** makes this easy by supporting installation from various
**origins**.

## Supported Sharing Methods

### 1. Git Repositories
The most robust way to share and version your **Tomes** is by hosting them in a
Git repository (like GitHub, GitLab, or a private server).

- **How to share:** Commit your **Tome** directory structure to a Git
  repository. A typical structure might look like:

```text
your-tome-repo
├── namespace_A
│   └── utility.py
├── namespace_B
│   ├── script1.py
│   └── script2.sh
├── README.md
└── requirements.txt
```

**Note on `.tomeignore`:** It's a good practice to Include a `.tomeignore` file
in your **Tome's** root to list files or patterns that **tome** should exclude
during installation, much like a `.gitignore`. This prevents unwanted items
(e.g., virtual environments, test artifacts, backups) from being included,
ensuring only necessary files are processed. Each line in `.tomeignore` defines
a pattern; lines starting with `#` are comments.

```bash
# .tomeignore example
*.log
temp_files/
__pycache__/
*.pyc
.venv/
my_secret_backup.txt
```

- **How users install:**
  To install the default branch:

  ```console
  $ tome install https://github.com/your-user/your-tome-repo.git
  ```

  They can also specify a particular **branch**, **tag**, or **commit hash** using the `@` symbol after the repository URL:

  * **Installing from a specific branch:**
      (e.g., to get scripts from a feature branch)

```console
$ tome install https://github.com/your-user/your-tome-repo.git@my-feature-branch
```

  * **Installing from a specific tag:**
      (e.g., to get a stable version like `v1.0.2`)

  ```console
  $ tome install https://github.com/your-user/your-tome-repo.git@v1.0.2
  ```

  * **Installing from a specific commit hash:**
      (e.g., to get scripts exactly as they were at a particular point in history)

  ```console
  $ tome install https://github.com/your-user/your-tome-repo.git@a1b2c3d4e5f60708090a0b0c0d0e0f0a0b0c0d0e
  ```

### 2. Local Folders
For sharing within a team on a shared drive or for distributing scripts that are
part of a larger local project:

- **How to share:** Ensure the directory containing your **Tome** (with its
  **Namespace** subdirectories) is accessible.

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
    - From a local file:

      ```console
      $ tome install /path/to/my-tome.zip
      ```

    - From a URL:

      ```console
      $ tome install https://example.com/my-tome.zip
      ```

## Installing from a Subfolder (`--folder` Option)
If your actual scripts within a Git repository or ZIP file are located in a
subdirectory (not at the root of the repository/archive), users can point
**tome** to it using the `--folder` flag during installation:

```console
$ tome install <git_or_zip_source> --folder path/to/scripts_within_source
```

For example, if your scripts are in an `src/` folder inside your Git repository:

```console
$ tome install https://github.com/your-user/your-tome-repo.git --folder src
```
