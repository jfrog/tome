# Welcome to **tome**

**tome** is a powerful script management tool designed to streamline the organization and
distribution of scripts across different environments. Built with flexibility and ease of
use in mind, **tome** enhances how scripts of any kind are managed, shared, tested, and
maintained.

## Why Use **tome**?

With **tome**, you gain:

- **Organization** 📂: Keep your scripts neatly structured for easy management and
  maintenance.
- **Collaboration** 🤝: Seamlessly share scripts with your team, improving productivity.
- **Testing** 🧪: Ensure script reliability with built-in testing tools.
- **Security** 🔐: Use **tome vaults** to manage secrets securely.

---

## Installation

The recommended way to install **tome** is using `pip` within a virtual environment. This
keeps your project dependencies isolated and manageable.

### 1. Create a Virtual Environment

```bash
python -m venv tome-env
```

### 2. Activate the Virtual Environment

#### On UNIX/macOS

```bash
source tome-env/bin/activate
```

#### On Windows

```bash
tome-env\Scripts\activate
```

### 3. Install **tome**

Once the virtual environment is activated, install **tome** with:

```bash
pip install tomescripts
```

---

## Getting Started

Now that **tome** is installed, you can verify the installation by running:

```bash
tome --help
```

This will display the available commands and usage options.

For a quick start, try listing all available commands:

```bash
tome list
```

To learn more about specific commands, check out the [Usage Guide](use_tome.md).
