# Glossary

Estos son algunos de los conceptos que puedes encontrar a lo largo de la documentación...

- **Tome command**: All the tome built-in commands like `tome install`, `tome
  list`, etc.
- **Tome**: It is the collection of **Scripts** that have a common **Origin** (a
  folder, a git repository, ...).
- **Origin**: site where a **Tome** comes from, it can be a git repository, a
  local folder or a zip file for example.
- **Namespace**: is the name of a **Tome**, it is used to group **Commands** and
  to be able to simply differentiate in a simple way two **Commands** with the
  same name. For example `foo:hello` and `bar:hello`, in this case `foo` and
  `bar` would be two **Namespaces** that both have a `hello` **Command**.
- **Command**: All the commands defined inside a **Tome** under a **Namespace**.
- **Script**: All files inside a **Tome** where the **Commands** are defined.
