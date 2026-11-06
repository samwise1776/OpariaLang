import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def compile_oparia(source, output=None):
    source = Path(source).resolve()

    if not source.is_file():
        raise SystemExit(f"Source not found: {source}")

    if source.suffix not in (".oparia", ".opa"):
        raise SystemExit("Expected a .oparia or .opa file")

    os_name = platform.system()

    if os_name not in ("Linux", "Windows", "Darwin"):
        raise SystemExit(f"Unsupported OS: {os_name}")

    suffix = ".exe" if os_name == "Windows" else ""
    destination = Path(output or source.stem).resolve()

    if os_name == "Windows" and destination.suffix.lower() != ".exe":
        destination = destination.with_suffix(".exe")

    if destination.exists() and destination.is_dir():
        raise SystemExit("Output path is a directory")

    if not shutil.which("gcc") and os_name == "Linux":
        raise SystemExit("GCC is required for Nuitka on Linux")

    try:
        import nuitka
    except ImportError:
        raise SystemExit(
            "Nuitka is not installed.\n"
            "Install with: python -m pip install nuitka"
        )

    with tempfile.TemporaryDirectory(prefix="oparia_build_") as temp:
        build = Path(temp)
        launcher = build / "oparia_launcher.py"

        source_copy = build / "program.oparia"
        shutil.copy2(source, source_copy)

        interpreter = ROOT / "main.py"
        extensions = ROOT / "lang_extensions.py"

        if not interpreter.exists():
            raise SystemExit("main.py not found")

        shutil.copy2(interpreter, build / "main.py")

        if extensions.exists():
            shutil.copy2(extensions, build / "lang_extensions.py")

        launcher.write_text(
            "import sys\n"
            "from pathlib import Path\n"
            "from main import logical_lines, execute\n"
            "import main\n"
            "source = Path(__file__).with_name('program.oparia')\n"
            "try:\n"
            "    execute(logical_lines(source.read_text(encoding='utf-8')))\n"
            "except main.LangError as error:\n"
            "    sys.exit(f'OpariaLang error: {error}')\n",
            encoding="utf-8",
        )

        command = [
            sys.executable,
            "-m",
            "nuitka",
            "--mode=onefile",
            "--assume-yes-for-downloads",
            "--output-dir=" + str(build / "output"),
            "--output-filename=" + destination.name,
            "--include-data-files="
            + str(source_copy)
            + "=program.oparia",
            str(launcher),
        ]

        print(f"Operating system: {os_name}")
        print(f"Architecture: {platform.machine()}")
        print(f"Source: {source}")
        print(f"Output: {destination}")
        print("Compiling native executable...")

        subprocess.run(command, check=True)

        built = build / "output" / destination.name

        if not built.exists():
            raise SystemExit("Nuitka did not produce the expected executable")

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(built, destination)

        if os_name != "Windows":
            destination.chmod(destination.stat().st_mode | 0o111)

        print(f"\nCompiled successfully: {destination}")
        print(f"Size: {destination.stat().st_size:,} bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="OpariaLang native executable compiler"
    )
    parser.add_argument("source", help="OpariaLang source file")
    parser.add_argument("-o", "--output", help="Executable output path")
    args = parser.parse_args()

    compile_oparia(args.source, args.output)
