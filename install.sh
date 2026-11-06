
#!/usr/bin/env bash

set -Eeuo pipefail

# ============================================
# OPARIALANG INSTALLER
# ============================================

APP_NAME="OpariaLang"
APP_ID="oparialang"

SOURCE_DIR="$(
    cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
    pwd -P
)"

DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
BIN_HOME="$HOME/.local/bin"

INSTALL_DIR="$DATA_HOME/$APP_ID"
BIN_FILE="$BIN_HOME/oparia"

# ============================================
# COLORS
# ============================================

if [[ -t 1 ]]; then
    GREEN=$'\033[32m'
    RED=$'\033[31m'
    BLUE=$'\033[34m'
    YELLOW=$'\033[33m'
    RESET=$'\033[0m'
else
    GREEN=""
    RED=""
    BLUE=""
    YELLOW=""
    RESET=""
fi

info() {
    printf '%s[OpariaLang]%s %s\n' \
        "$BLUE" "$RESET" "$*"
}

success() {
    printf '%s[OK]%s %s\n' \
        "$GREEN" "$RESET" "$*"
}

warning() {
    printf '%s[WARNING]%s %s\n' \
        "$YELLOW" "$RESET" "$*" >&2
}

fail() {
    printf '%s[ERROR]%s %s\n' \
        "$RED" "$RESET" "$*" >&2
    exit 1
}

# ============================================
# DEPENDENCIES
# ============================================

check_dependencies() {
    command -v python3 >/dev/null 2>&1 ||
        fail "Python 3 is not installed."

    python3 -m venv --help >/dev/null 2>&1 ||
        fail "Python venv is unavailable."

    if ! command -v gcc >/dev/null 2>&1; then
        warning "GCC missing. External C compilation will be unavailable."
    fi

    if ! command -v g++ >/dev/null 2>&1; then
        warning "G++ missing. External C++ compilation will be unavailable."
    fi
}

# ============================================
# COPY FILES
# ============================================

copy_file() {
    local filename="$1"

    if [[ -f "$SOURCE_DIR/$filename" ]]; then
        install -m 644 \
            "$SOURCE_DIR/$filename" \
            "$INSTALL_DIR/$filename"

        success "Installed $filename"
    else
        warning "Optional file missing: $filename"
    fi
}

copy_directory() {
    local dirname="$1"

    if [[ -d "$SOURCE_DIR/$dirname" ]]; then
        mkdir -p "$INSTALL_DIR/$dirname"

        cp -a \
            "$SOURCE_DIR/$dirname/." \
            "$INSTALL_DIR/$dirname/"

        success "Installed $dirname/"
    fi
}

install_files() {
    info "Installing application files..."

    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_HOME"

    [[ -f "$SOURCE_DIR/main.py" ]] ||
        fail "main.py not found."

    # Never copy an active virtual environment.
    # It must be recreated at its final destination.

    copy_file "main.py"
    copy_file "compiler.py"
    copy_file "lang_extensions.py"
    copy_file "SYNTAX.md"
    copy_file "README.md"
    copy_file "requirements.txt"

    copy_directory "examples"
    copy_directory "vscode-extension"

    # Python cache and virtual environments
    # from the source tree are unnecessary.

    find "$INSTALL_DIR" \
        -path "$INSTALL_DIR/.venv" -prune -o \
        -type d -name "__pycache__" \
        -prune -exec rm -rf {} +

    success "Application files installed."
}

# ============================================
# PYTHON ENVIRONMENT
# ============================================

install_python_environment() {
    info "Preparing Python environment..."

    # --system-site-packages allows access to
    # GTK4 PyGObject installed by the OS.

    if [[ ! -x "$INSTALL_DIR/.venv/bin/python" ]]; then
        python3 -m venv \
            --system-site-packages \
            "$INSTALL_DIR/.venv"
    fi

    local python="$INSTALL_DIR/.venv/bin/python"

    [[ -x "$python" ]] ||
        fail "Could not create Python environment."

    success "Created Python environment."

    if [[ -f "$INSTALL_DIR/requirements.txt" ]]; then
        info "Installing Python requirements..."

        "$python" -m pip install \
            -r "$INSTALL_DIR/requirements.txt" ||
            fail "Could not install requirements."
    fi

    "$python" -m py_compile \
        "$INSTALL_DIR/main.py" ||
        fail "main.py contains a syntax error."

    if [[ -f "$INSTALL_DIR/compiler.py" ]]; then
        "$python" -m py_compile \
            "$INSTALL_DIR/compiler.py" ||
            fail "compiler.py contains a syntax error."
    fi

    success "Python source verified."
}

# ============================================
# CREATE GLOBAL USER COMMAND
# ============================================

install_launcher() {
    info "Creating oparia command..."

    cat > "$BIN_FILE" <<'LAUNCHER'
#!/usr/bin/env bash

set -euo pipefail

DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
ROOT="$DATA_HOME/oparialang"

PYTHON="$ROOT/.venv/bin/python"
INTERPRETER="$ROOT/main.py"
COMPILER="$ROOT/compiler.py"

if [[ ! -x "$PYTHON" ]]; then
    echo "OpariaLang Python environment missing." >&2
    exit 1
fi

if [[ ! -f "$INTERPRETER" ]]; then
    echo "OpariaLang interpreter missing." >&2
    exit 1
fi

show_help() {
    cat <<'HELP'
OpariaLang Programming Language

Usage:
  oparia <file.oparia>
  oparia run <file.oparia>
  oparia compile <file.oparia>
  oparia compile <file.oparia> -o <output>
  oparia syntax
  oparia examples
  oparia version
  oparia help

Commands:
  run       Execute an OpariaLang file
  compile   Compile to a native executable
  syntax    Open/show the language reference
  examples  Display installed examples
  version   Display OpariaLang version
  help      Display this help

Project:
  ~/.local/share/oparialang/

HELP
}

if [[ $# -eq 0 ]]; then
    show_help
    exit 0
fi

COMMAND="$1"
shift

case "$COMMAND" in

    help|--help|-h)
        show_help
        ;;

    version|--version|-v)
        echo "OpariaLang 0.1.0"
        ;;

    run)
        if [[ $# -eq 0 ]]; then
            echo "Usage: oparia run <file>" >&2
            exit 1
        fi

        exec "$PYTHON" "$INTERPRETER" "$@"
        ;;

    compile|build)
        if [[ $# -eq 0 ]]; then
            echo "Usage: oparia compile <file> [-o output]" >&2
            exit 1
        fi

        if [[ ! -f "$COMPILER" ]]; then
            echo "Native compiler is not installed." >&2
            exit 1
        fi

        exec "$PYTHON" "$COMPILER" "$@"
        ;;

    syntax|docs)
        DOC="$ROOT/SYNTAX.md"

        [[ -f "$DOC" ]] || {
            echo "SYNTAX.md missing." >&2
            exit 1
        }

        if command -v less >/dev/null 2>&1; then
            exec less "$DOC"
        else
            exec cat "$DOC"
        fi
        ;;

    examples)
        if [[ -d "$ROOT/examples" ]]; then
            ls -la "$ROOT/examples"
        else
            echo "No examples installed."
        fi
        ;;

    *)
        # Treat the first argument as a filename.
        exec "$PYTHON" "$INTERPRETER" \
            "$COMMAND" "$@"
        ;;

esac
LAUNCHER

    chmod 755 "$BIN_FILE"

    success "Created $BIN_FILE"
}

# ============================================
# PATH CONFIGURATION
# ============================================

configure_path() {
    info "Checking PATH..."

    case ":$PATH:" in
        *":$BIN_HOME:"*)
            success "~/.local/bin is already in PATH."
            ;;
        *)
            warning "~/.local/bin is not currently in PATH."

            # Add a guarded PATH entry to bash startup.
            local bashrc="$HOME/.bashrc"

            if ! grep -Fq \
                'export PATH="$HOME/.local/bin:$PATH"' \
                "$bashrc" 2>/dev/null; then

                cat >> "$bashrc" <<'PATHLINE'

# OpariaLang user commands
export PATH="$HOME/.local/bin:$PATH"
PATHLINE

                success "Updated ~/.bashrc"
            fi

            warning "For this terminal, run:"
            echo 'export PATH="$HOME/.local/bin:$PATH"'
            ;;
    esac
}

# ============================================
# OPTIONAL NATIVE COMPILER DEPENDENCY
# ============================================

install_compiler_dependency() {
    local python="$INSTALL_DIR/.venv/bin/python"

    if [[ ! -f "$INSTALL_DIR/compiler.py" ]]; then
        return
    fi

    if "$python" -c "import nuitka" \
        >/dev/null 2>&1; then
        success "Nuitka is available."
        return
    fi

    info "Installing Nuitka native compiler..."

    if "$python" -m pip install \
        nuitka ordered-set zstandard; then

        success "Nuitka installed."
    else
        warning "Nuitka installation failed."
        warning "Interpreter installed; native compilation unavailable."
    fi
}

# ============================================
# VERIFY
# ============================================

verify_installation() {
    info "Verifying installation..."

    [[ -x "$BIN_FILE" ]] ||
        fail "Launcher is not executable."

    [[ -f "$INSTALL_DIR/main.py" ]] ||
        fail "Interpreter missing."

    [[ -x "$INSTALL_DIR/.venv/bin/python" ]] ||
        fail "Python environment missing."

    "$BIN_FILE" version

    success "Installation verified."
}

# ============================================
# UNINSTALL
# ============================================

uninstall_oparia() {
    echo
    warning "This will remove the installed OpariaLang files:"
    echo "  $INSTALL_DIR"
    echo "  $BIN_FILE"
    echo
    echo "Your source repository will not be deleted."
    echo

    read -r -p "Type UNINSTALL to continue: " answer

    [[ "$answer" == "UNINSTALL" ]] ||
        fail "Uninstall cancelled."

    rm -f -- "$BIN_FILE"
    rm -rf -- "$INSTALL_DIR"

    success "OpariaLang uninstalled."
}

# ============================================
# MAIN
# ============================================

main() {
    if [[ "${1:-}" == "--uninstall" ]]; then
        uninstall_oparia
        exit 0
    fi

    echo
    echo "========================================"
    echo "        OPARIALANG INSTALLER"
    echo "========================================"
    echo

    echo "Source:  $SOURCE_DIR"
    echo "Install: $INSTALL_DIR"
    echo "Binary:  $BIN_FILE"
    echo

    check_dependencies
    install_files
    install_python_environment
    install_compiler_dependency
    install_launcher
    configure_path
    verify_installation

    echo
    echo "========================================"
    echo "      INSTALLATION COMPLETED"
    echo "========================================"
    echo

    echo "Try:"
    echo "  oparia help"
    echo "  oparia version"
    echo "  oparia examples"
    echo "  oparia examples/hello.oparia"
    echo "  oparia compile examples/hello.oparia -o hello"
    echo

    echo "Installed to:"
    echo "  $INSTALL_DIR"
    echo

    echo "Launcher:"
    echo "  $BIN_FILE"
    echo

    success "OpariaLang is installed!"
}

main "$@"
