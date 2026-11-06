# OpariaLang

OpariaLang is a custom programming language implemented in Python.

## Features

- Typed variables
- Lists and dictionaries
- Strings and f-strings
- Arithmetic and boolean expressions
- Conditions and loops
- Functions and return values
- File operations
- System commands
- External Python, C, and C++ execution
- Optional GUI, namespace, class and library extensions
- VS Code extension with syntax highlighting and autocomplete

## Run a program

```bash
.venv/bin/python main.py examples/hello.oparia
```

## VS Code

Open `vscode-extension/` in VS Code and press F5.

The extension includes language highlighting, completions, snippets,
basic diagnostics and an OpariaLang Run File command.

## Syntax

See [SYNTAX.md](SYNTAX.md).

## Requirements

- Python 3
- GCC for C extern blocks
- G++ for C++ extern blocks
- Optional GTK4/PyGObject for GUI support

## License

MIT
