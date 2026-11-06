# OpariaLang VS Code Extension

Provides:

- Syntax highlighting for OpariaLang
- Code snippets and completions
- File associations for `.oparia` and `.opa`
- Automatic bracket pairing and indentation
- Basic unmatched-block diagnostics
- Run File command
- Python/C/C++ extern syntax recognition
- File and GUI API completion candidates

## Local installation

Open this extension directory in VS Code and press F5
to start an Extension Development Host.

Alternatively, package it with `vsce` and install the VSIX.

## Run

Open an `.oparia` file and choose:

**OpariaLang: Run File**

The extension finds `main.py` and uses the Python interpreter
from `.venv` when one exists.

## Notes

GUI completions describe potential API names. Their runtime support
depends on `lang_extensions.py`.

Diagnostics are lightweight syntax checks, not full parsing or
type checking.

The extension recognizes external-language blocks but does not
provide a complete embedded C/C++/Python language server.
