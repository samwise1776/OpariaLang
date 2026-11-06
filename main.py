
import ast
import operator
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    import lang_extensions as _lang_ext
except ImportError:
    _lang_ext = None


# ============================================
# GLOBAL STATE
# ============================================

variables = {}
types = {}
functions = {}
extern_functions = {}

MAX_LOOP = 1_000_000

if _lang_ext is not None:
    for name in (
        "gui",
        "namespace",
        "create_class",
        "load_library",
    ):
        if hasattr(_lang_ext, name):
            variables[name] = getattr(_lang_ext, name)


# ============================================
# ERRORS AND CONTROL FLOW
# ============================================

class LangError(Exception):
    pass


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class ReturnSignal(Exception):
    def __init__(self, value):
        super().__init__("return")
        self.value = value


def sleep(seconds):
    seconds = float(seconds)

    if not 0 <= seconds <= 86400:
        raise LangError(
            "wait() expects 0 to 86400 seconds"
        )

    time.sleep(seconds)


# ============================================
# SYSTEM AND EXTERNAL LANGUAGES
# ============================================

def system(command, capture=False, check=False):
    """
    Execute a shell command.

    system("echo Hello")
    system("ls -la")
    system("pwd", true)
    """

    command = str(command)

    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=bool(capture),
            check=False,
        )
    except OSError as error:
        raise LangError(
            f"System execution failed: {error}"
        ) from error

    if check and result.returncode != 0:
        raise LangError(
            f"System command failed with "
            f"exit code {result.returncode}: {command}"
        )

    if capture:
        return result.stdout

    return result.returncode


def run_native(language, source):
    """
    Compile and run a C or C++ program.

    A full program with main() is supported.
    A block without main() is placed inside
    an automatically generated main().
    """

    if language == "C":
        compiler = "gcc"
        extension = ".c"
    elif language == "C++":
        compiler = "g++"
        extension = ".cpp"
    else:
        raise LangError(
            f"Unsupported native language: {language}"
        )

    if not re.search(
        r"\bmain\s*\(",
        source
    ):
        if language == "C":
            source = (
                "#include <stdio.h>\n"
                "#include <stdlib.h>\n"
                "#include <string.h>\n"
                "int main(void) {\n"
                + source +
                "\nreturn 0;\n}\n"
            )
        else:
            source = (
                "#include <iostream>\n"
                "#include <string>\n"
                "#include <vector>\n"
                "using namespace std;\n"
                "int main() {\n"
                + source +
                "\nreturn 0;\n}\n"
            )

    with tempfile.TemporaryDirectory(
        prefix="lang_extern_"
    ) as directory:
        folder = Path(directory)

        source_file = folder / (
            "program" + extension
        )
        executable = folder / "program"

        source_file.write_text(
            source,
            encoding="utf-8"
        )

        try:
            compiled = subprocess.run(
                [
                    compiler,
                    str(source_file),
                    "-o",
                    str(executable),
                ],
                text=True,
                capture_output=True,
            )
        except FileNotFoundError as error:
            raise LangError(
                f"{compiler} is not installed"
            ) from error

        if compiled.returncode != 0:
            raise LangError(
                f"{language} compilation failed:\n"
                + compiled.stderr
            )

        result = subprocess.run(
            [str(executable)],
            text=True,
            capture_output=True,
        )

        if result.stdout:
            print(result.stdout, end="")

        if result.stderr:
            print(
                result.stderr,
                end="",
                file=sys.stderr
            )

        return result.returncode


def run_python(source):
    """
    Run trusted Python source inside the
    interpreter, sharing language variables.
    """

    scope = {
        "__builtins__": __builtins__,
        "variables": variables,
        "types": types,
        "functions": functions,
        "system": system,
    }

    for name, value in variables.items():
        if name.isidentifier():
            scope[name] = value

    original = set(scope)

    try:
        exec(source, scope, scope)
    except Exception as error:
        raise LangError(
            f"Python extern error: {error}"
        ) from error

    for name, value in scope.items():
        if name.startswith("_"):
            continue

        if name in (
            "__builtins__",
            "variables",
            "types",
            "functions",
            "system",
        ):
            continue

        if name in variables:
            spec = types.get(name, "any")

            if not check(value, spec):
                raise LangError(
                    f"Python changed {name} to "
                    f"an incompatible type"
                )

        variables[name] = value
        types.setdefault(name, "any")

    return None


def run_extern(language, source):
    language = language.strip().lower()

    if language == "python":
        return run_python(source)

    if language == "c":
        return run_native("C", source)

    if language in ("c++", "cpp"):
        return run_native("C++", source)

    raise LangError(
        f"Unknown extern language: {language}"
    )


# ============================================
# FILE FUNCTIONS
# ============================================

class File:
    @staticmethod
    def write(filename, content):
        Path(str(filename)).write_text(
            str(content),
            encoding="utf-8"
        )

    @staticmethod
    def append(filename, content):
        with open(
            str(filename),
            "a",
            encoding="utf-8"
        ) as file:
            file.write(str(content))

    @staticmethod
    def read(filename):
        return Path(str(filename)).read_text(
            encoding="utf-8"
        )

    @staticmethod
    def exists(filename):
        return Path(str(filename)).exists()

    @staticmethod
    def delete(filename):
        Path(str(filename)).unlink()

    @staticmethod
    def mkdir(dirname):
        Path(str(dirname)).mkdir(
            parents=True,
            exist_ok=True
        )

    @staticmethod
    def size(filename):
        return Path(str(filename)).stat().st_size


FILE_METHODS = {
    "write": File.write,
    "append": File.append,
    "read": File.read,
    "exists": File.exists,
    "delete": File.delete,
    "mkdir": File.mkdir,
    "size": File.size,
}


# ============================================
# BUILTIN FUNCTIONS
# ============================================

BUILTINS = {
    "len": len,
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "range": lambda *a: list(range(*a)),
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "round": round,
    "input": input,
    "wait": sleep,
    "sleep": sleep,
    "system": system,
    "upper": lambda s: str(s).upper(),
    "lower": lambda s: str(s).lower(),
    "strip": lambda s: str(s).strip(),
    "replace": lambda s, a, b: str(s).replace(
        str(a), str(b)
    ),
    "split": lambda s, sep=None: str(s).split(sep),
    "join": lambda sep, items: str(sep).join(
        map(str, items)
    ),
    "contains": lambda obj, item: item in obj,
    "keys": lambda d: list(d.keys()),
    "values": lambda d: list(d.values()),
    "items": lambda d: list(d.items()),
    "list": list,
    "dict": dict,
    "print": print,
}


# ============================================
# STRING AND PARSING UTILITIES
# ============================================

def split_top(text, separator=","):
    parts = []
    start = 0
    stack = []
    quote = None
    escaped = False

    opening = {
        "(": ")",
        "[": "]",
        "{": "}",
    }

    for i, char in enumerate(text):
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue

        if char in ('"', "'"):
            quote = char

        elif char in opening:
            stack.append(opening[char])

        elif char in ")]}":
            if not stack or stack.pop() != char:
                raise LangError("Unmatched bracket")

        elif char == separator and not stack:
            parts.append(text[start:i].strip())
            start = i + 1

    if quote is not None:
        raise LangError("Unclosed string")

    if stack:
        raise LangError("Unclosed bracket")

    parts.append(text[start:].strip())

    return parts


def normalize(expr):
    pattern = re.compile(
        r"""("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')"""
        r"""|\b(true|false|null)\b""",
        re.S
    )

    replacements = {
        "true": "True",
        "false": "False",
        "null": "None",
    }

    def replace(match):
        if match.group(1) is not None:
            return match.group(1)

        return replacements[match.group(2)]

    return pattern.sub(replace, expr)


def display(value):
    if isinstance(value, bool):
        return str(value).lower()

    if value is None:
        return "null"

    if isinstance(value, list):
        return "[" + ", ".join(
            display(item) for item in value
        ) + "]"

    if isinstance(value, dict):
        return "{" + ", ".join(
            f"{display(key)}: {display(item)}"
            for key, item in value.items()
        ) + "}"

    return str(value)


# ============================================
# TYPE SYSTEM
# ============================================

def canonical_type(spec):
    spec = spec.strip()

    if spec == "text":
        return "string"

    return spec


def check(value, spec):
    spec = canonical_type(spec)

    if spec == "any":
        return True

    if spec == "int":
        return type(value) is int

    if spec == "float":
        return type(value) in (int, float)

    if spec == "string":
        return isinstance(value, str)

    if spec == "bool":
        return type(value) is bool

    if spec == "null":
        return value is None

    if (
        spec.startswith("list<")
        and spec.endswith(">")
    ):
        parameters = split_top(spec[5:-1])

        if len(parameters) == 1:
            return (
                isinstance(value, list)
                and all(
                    check(item, parameters[0])
                    for item in value
                )
            )

        if len(parameters) == 2:
            return (
                isinstance(value, dict)
                and all(
                    check(key, parameters[0])
                    and check(item, parameters[1])
                    for key, item in value.items()
                )
            )

    return False


def assign(name, value, declared=None):
    if declared is not None:
        declared = canonical_type(declared)

        if name in variables:
            raise LangError(
                f"Already declared: {name}"
            )

        if not check(value, declared):
            raise LangError(
                f"Type mismatch: {name} expects "
                f"{declared}, got {value!r}"
            )

        types[name] = declared

    elif name not in variables:
        raise LangError(
            f"Unknown variable: {name}"
        )

    spec = types.get(name, "any")

    if not check(value, spec):
        raise LangError(
            f"Type mismatch: {name} expects "
            f"{spec}, got {value!r}"
        )

    if spec == "float":
        value = float(value)

    variables[name] = value


# ============================================
# EXPRESSION EVALUATOR
# ============================================

def evaluate(expr):
    expr = expr.strip()

    try:
        tree = ast.parse(
            normalize(expr),
            mode="eval"
        )
    except SyntaxError as error:
        raise LangError(
            f"Invalid expression: {expr}"
        ) from error

    def ev(node):
        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Name):
            if node.id in variables:
                return variables[node.id]

            raise LangError(
                f"Unknown variable: {node.id}"
            )

        if isinstance(node, ast.List):
            return [
                ev(item) for item in node.elts
            ]

        if isinstance(node, ast.Tuple):
            return tuple(
                ev(item) for item in node.elts
            )

        if isinstance(node, ast.Dict):
            result = {}

            for key, value in zip(
                node.keys, node.values
            ):
                if key is None:
                    raise LangError(
                        "Dictionary unpacking unsupported"
                    )

                result[ev(key)] = ev(value)

            return result

        if isinstance(node, ast.Subscript):
            obj = ev(node.value)

            if isinstance(node.slice, ast.Slice):
                start = (
                    ev(node.slice.lower)
                    if node.slice.lower else None
                )
                stop = (
                    ev(node.slice.upper)
                    if node.slice.upper else None
                )
                step = (
                    ev(node.slice.step)
                    if node.slice.step else None
                )

                return obj[slice(start, stop, step)]

            return obj[ev(node.slice)]

        if isinstance(node, ast.JoinedStr):
            return "".join(
                str(ev(part))
                for part in node.values
            )

        if isinstance(node, ast.FormattedValue):
            value = ev(node.value)

            if node.conversion == 114:
                value = repr(value)
            elif node.conversion == 97:
                value = ascii(value)
            elif node.conversion == 115:
                value = str(value)

            if node.format_spec is not None:
                value = format(
                    value,
                    ev(node.format_spec)
                )

            return value

        if isinstance(node, ast.BinOp):
            operations = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.FloorDiv: operator.floordiv,
                ast.Mod: operator.mod,
                ast.Pow: operator.pow,
            }

            operation = operations.get(type(node.op))

            if operation is None:
                raise LangError(
                    "Unsupported arithmetic operator"
                )

            return operation(
                ev(node.left),
                ev(node.right)
            )

        if isinstance(node, ast.UnaryOp):
            value = ev(node.operand)

            if isinstance(node.op, ast.Not):
                return not value

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return +value

            raise LangError(
                "Unsupported unary operator"
            )

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                value = True

                for item in node.values:
                    value = ev(item)

                    if not value:
                        return value

                return value

            if isinstance(node.op, ast.Or):
                value = False

                for item in node.values:
                    value = ev(item)

                    if value:
                        return value

                return value

        if isinstance(node, ast.Compare):
            operations = {
                ast.Eq: operator.eq,
                ast.NotEq: operator.ne,
                ast.Lt: operator.lt,
                ast.LtE: operator.le,
                ast.Gt: operator.gt,
                ast.GtE: operator.ge,
                ast.In: lambda a, b: a in b,
                ast.NotIn: lambda a, b: a not in b,
                ast.Is: operator.is_,
                ast.IsNot: operator.is_not,
            }

            left = ev(node.left)

            for op, right_node in zip(
                node.ops, node.comparators
            ):
                right = ev(right_node)
                operation = operations.get(type(op))

                if operation is None:
                    raise LangError(
                        "Unsupported comparison"
                    )

                if not operation(left, right):
                    return False

                left = right

            return True

        if isinstance(node, ast.Attribute):
            obj = ev(node.value)

            if node.attr.startswith("_"):
                raise LangError(
                    "Private attribute unavailable"
                )

            allowed = False

            if _lang_ext is not None:
                allowed_types = tuple(
                    getattr(_lang_ext, name)
                    for name in (
                        "GUI",
                        "Namespace",
                        "LangClass",
                    )
                    if isinstance(
                        getattr(_lang_ext, name, None),
                        type
                    )
                )

                if isinstance(obj, allowed_types):
                    allowed = True

                if obj is _lang_ext:
                    allowed = True

                if getattr(
                    obj, "__name__", ""
                ).startswith("local_lang_"):
                    allowed = True

            if obj is File:
                allowed = True

            if not allowed:
                raise LangError(
                    "Unsupported attribute access"
                )

            return getattr(obj, node.attr)

        if isinstance(node, ast.Call):
            args = [
                ev(arg) for arg in node.args
            ]
            kwargs = {}

            for keyword in node.keywords:
                if keyword.arg is None:
                    raise LangError(
                        "**kwargs is unsupported"
                    )

                if keyword.arg in kwargs:
                    raise LangError(
                        "Duplicate argument: "
                        + keyword.arg
                    )

                kwargs[keyword.arg] = ev(keyword.value)

            if isinstance(node.func, ast.Attribute):
                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "File"
                ):
                    method = node.func.attr

                    if method not in FILE_METHODS:
                        raise LangError(
                            "Unknown File method: " + method
                        )

                    return FILE_METHODS[method](
                        *args, **kwargs
                    )

                target = ev(node.func)

                if not callable(target):
                    raise LangError(
                        "Attribute is not callable"
                    )

                return target(*args, **kwargs)

            if not isinstance(node.func, ast.Name):
                raise LangError(
                    "Invalid function call"
                )

            name = node.func.id

            if name in BUILTINS:
                return BUILTINS[name](
                    *args, **kwargs
                )

            if name in variables and callable(
                variables[name]
            ):
                return variables[name](
                    *args, **kwargs
                )

            if name in functions:
                return call_function(
                    name, args, kwargs
                )

            raise LangError(
                f"Unknown function: {name}"
            )

        raise LangError(
            "Unsupported expression: "
            + ast.dump(node)
        )

    try:
        return ev(tree.body)
    except (
        LangError,
        ReturnSignal,
        BreakSignal,
        ContinueSignal,
    ):
        raise
    except Exception as error:
        raise LangError(
            f"Expression error in {expr!r}: {error}"
        ) from error


# ============================================
# COLLECTIONS
# ============================================

def collection(expr):
    inner = expr.strip()[1:-1].strip()

    if not inner:
        return []

    parts = [
        part
        for part in split_top(inner)
        if part
    ]

    pairs = [
        split_top(part, ":")
        for part in parts
    ]

    if all(len(pair) == 2 for pair in pairs):
        return {
            value_of(key): value_of(value)
            for key, value in pairs
        }

    if all(len(pair) == 1 for pair in pairs):
        return [
            value_of(pair[0])
            for pair in pairs
        ]

    raise LangError(
        "Mixed list and dictionary entries"
    )


def value_of(expr):
    expr = expr.strip()

    if (
        expr.startswith("{")
        and expr.endswith("}")
    ):
        return collection(expr)

    return evaluate(expr)


# ============================================
# SOURCE PROCESSING
# ============================================

def brace_balance(text):
    depth = 0
    quote = None
    escaped = False

    for char in text:
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue

        if char in ('"', "'"):
            quote = char

        elif char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

    return depth


def logical_lines(source):
    lines = []
    pending = ""
    depth = 0
    in_extern = False
    extern_depth = 0
    extern_language = ''

    declaration_pattern = re.compile(
        r"^(?:list<[^>]+>|string|text|int|float|bool|any)"
        r"\s+\w+\s*=\s*\{"
    )
    assignment_pattern = re.compile(
        r"^[A-Za-z_]\w*\s*=\s*\{"
    )

    for raw in source.splitlines():
        line = raw.strip()

        if in_extern:
            lines.append(raw)

            if extern_language.lower() == "python":
                if line == "}":
                    in_extern = False
            else:
                extern_depth += brace_balance(raw)
                if extern_depth == 0:
                    in_extern = False

            continue

        if not line:
            continue

        if line.startswith(("#", "//")):
            continue

        if re.fullmatch(
            r'extern\s+["\'](?:Python|C|C\+\+|cpp)["\']\s*\{',
            line,
            re.I
        ):
            lines.append(line)
            in_extern = True
            extern_depth = 1
            extern_language = re.search(
                r'extern\\s+["\\\']([^"\\\']+)["\\\']',
                line,
                re.I
            ).group(1)
            continue

        if pending:
            pending += "\n" + line
            depth += brace_balance(line)

            if depth == 0:
                lines.append(pending)
                pending = ""
            elif depth < 0:
                raise LangError(
                    "Unexpected closing brace"
                )

            continue

        is_collection = (
            declaration_pattern.match(line)
            or assignment_pattern.match(line)
        )

        if is_collection and brace_balance(line) > 0:
            pending = line
            depth = brace_balance(line)
        else:
            lines.append(line)

    if pending:
        raise LangError(
            "Unclosed collection"
        )

    if in_extern:
        raise LangError(
            "Unclosed extern block"
        )

    return lines


# ============================================
# BLOCK PARSING
# ============================================

def is_block_start(line):
    line = line.strip()

    if not line.endswith("{"):
        return False

    return (
        line.startswith((
            "if ",
            "elsif ",
            "while ",
            "repeat ",
            "for ",
            "func ",
        ))
        or line == "else {"
    )


def find_end(lines, start):
    depth = 0

    for index in range(start, len(lines)):
        line = lines[index].strip()

        if is_block_start(line):
            depth += 1

        if (
            line == "}"
            or line.startswith(("} else", "} elsif"))
        ):
            depth -= 1

            if depth == 0:
                return index

    raise LangError(
        f"Unclosed block at line {start + 1}"
    )


def parse_branches(lines, start):
    branches = []
    header = lines[start].strip()
    body_start = start + 1
    depth = 1
    index = body_start

    while index < len(lines):
        line = lines[index].strip()

        boundary = (
            line == "}"
            or line.startswith("} elsif ")
            or line.startswith("} else")
        )

        if depth == 1 and boundary:
            if header.startswith("if "):
                condition = header[3:-1].strip()

            elif header.startswith("elsif "):
                condition = header[6:-1].strip()

            elif header.startswith("else"):
                condition = None

            else:
                raise LangError(
                    "Invalid if branch"
                )

            branches.append(
                (condition, lines[body_start:index])
            )

            if line == "}":
                next_index = index + 1

                if next_index < len(lines):
                    next_line = lines[
                        next_index
                    ].strip()

                    if next_line.startswith(
                        ("elsif ", "else ")
                    ):
                        header = next_line
                        body_start = next_index + 1
                        index = next_index + 1
                        continue

                return branches, next_index

            header = line[2:].strip()
            body_start = index + 1
            index += 1
            continue

        if is_block_start(line):
            depth += 1

        if line == "}":
            depth -= 1

        index += 1

    raise LangError(
        "Unclosed if block"
    )


# ============================================
# USER FUNCTIONS
# ============================================

def call_function(name, args, kwargs=None):
    kwargs = dict(kwargs or {})

    if name not in functions:
        raise LangError(
            f"Unknown function: {name}"
        )

    parameters, body = functions[name]

    if len(args) > len(parameters):
        raise LangError(
            f"{name} accepts at most "
            f"{len(parameters)} arguments"
        )

    bound = {}

    for index, value in enumerate(args):
        param_name = parameters[index][0]
        bound[param_name] = value

    valid_names = [
        param_name
        for param_name, _ in parameters
    ]

    for key, value in kwargs.items():
        if key not in valid_names:
            raise LangError(
                f"Unknown argument: {key}"
            )

        if key in bound:
            raise LangError(
                f"Duplicate argument: {key}"
            )

        bound[key] = value

    for param_name, default in parameters:
        if param_name not in bound:
            if default is None:
                raise LangError(
                    f"Missing argument: {param_name}"
                )

            bound[param_name] = value_of(default)

    previous = {}

    for param_name, _ in parameters:
        previous[param_name] = (
            param_name in variables,
            variables.get(param_name),
            types.get(param_name)
        )

        variables[param_name] = bound[param_name]
        types[param_name] = "any"

    result = None

    try:
        try:
            execute(body)
        except ReturnSignal as returned:
            result = returned.value
        except (BreakSignal, ContinueSignal):
            raise LangError(
                "break/continue outside a loop"
            )
    finally:
        for param_name, _ in parameters:
            existed, old_value, old_type = (
                previous[param_name]
            )

            if existed:
                variables[param_name] = old_value

                if old_type is None:
                    types.pop(param_name, None)
                else:
                    types[param_name] = old_type
            else:
                variables.pop(param_name, None)
                types.pop(param_name, None)

    return result


# ============================================
# MAIN INTERPRETER
# ============================================

def execute(lines):
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # ====================================
        # EXTERN PYTHON / C / C++
        # ====================================


        extern_match = re.fullmatch(
            r'extern\\s+["\\\'](Python|C|C\\+\\+|cpp)["\\\']\\s*\\{',
            line,
            re.I
        )

        if extern_match:
            language = extern_match.group(1)
            body = []
            depth = 1
            i += 1

            while i < len(lines):
                raw = lines[i]
                stripped = raw.strip()

                if language.lower() == "python":
                    if stripped == "}":
                        depth -= 1
                    else:
                        body.append(raw)
                else:
                    depth += brace_balance(raw)

                    if depth > 0:
                        body.append(raw)

                if depth == 0:
                    break

                i += 1

            if depth != 0:
                raise LangError(
                    f"Unclosed extern {language} block"
                )

            run_extern(language, "\\n".join(body))
            i += 1
            continue

        if line == "}":
            raise LangError(
                "Unexpected closing brace"
            )

        # ====================================
        # IF / ELSIF / ELSE
        # ====================================

        if (
            line.startswith("if ")
            and line.endswith("{")
        ):
            branches, i = parse_branches(
                lines, i
            )

            for condition, body in branches:
                if (
                    condition is None
                    or evaluate(condition)
                ):
                    execute(body)
                    break

            continue

        # ====================================
        # WHILE / REPEAT / FOR
        # ====================================

        if (
            line.startswith(
                ("while ", "repeat ", "for ")
            )
            and line.endswith("{")
        ):
            end = find_end(lines, i)
            body = lines[i + 1:end]

            if line.startswith("while "):
                condition = line[6:-1].strip()
                steps = 0

                while evaluate(condition):
                    steps += 1

                    if steps > MAX_LOOP:
                        raise LangError(
                            "Loop exceeded "
                            "1,000,000 iterations"
                        )

                    try:
                        execute(body)
                    except ContinueSignal:
                        continue
                    except BreakSignal:
                        break

            elif line.startswith("repeat "):
                count = value_of(
                    line[7:-1].strip()
                )

                if (
                    type(count) is not int
                    or count < 0
                    or count > MAX_LOOP
                ):
                    raise LangError(
                        "Invalid repeat count"
                    )

                for iteration in range(count):
                    variables["i"] = iteration
                    types["i"] = "int"

                    try:
                        execute(body)
                    except ContinueSignal:
                        continue
                    except BreakSignal:
                        break

            else:
                match = re.fullmatch(
                    r"for\s+([A-Za-z_]\w*)"
                    r"\s+in\s+(.+?)\s*\{",
                    line,
                    re.S
                )

                if not match:
                    raise LangError(
                        "Invalid for loop"
                    )

                name, expression = match.groups()
                iterable = value_of(expression)

                try:
                    iterator = iter(iterable)
                except TypeError:
                    raise LangError(
                        "for requires an iterable"
                    )

                steps = 0

                for item in iterator:
                    steps += 1

                    if steps > MAX_LOOP:
                        raise LangError(
                            "Loop exceeded "
                            "1,000,000 iterations"
                        )

                    variables[name] = item
                    types[name] = "any"

                    try:
                        execute(body)
                    except ContinueSignal:
                        continue
                    except BreakSignal:
                        break

            i = end + 1
            continue

        # ====================================
        # FUNCTION DECLARATIONS
        # ====================================

        if (
            line.startswith("func ")
            and line.endswith("{")
        ):
            match = re.fullmatch(
                r"func\s+([A-Za-z_]\w*)"
                r"\((.*)\)\s*\{",
                line,
                re.S
            )

            if not match:
                raise LangError(
                    "Invalid function declaration"
                )

            end = find_end(lines, i)
            function_name = match.group(1)
            parameters = []

            for raw in split_top(match.group(2)):
                if not raw:
                    continue

                pieces = raw.split("=", 1)
                param_name = pieces[0].strip()

                default = (
                    pieces[1].strip()
                    if len(pieces) == 2
                    else None
                )

                if not param_name.isidentifier():
                    raise LangError(
                        "Invalid parameter name: "
                        + param_name
                    )

                if any(
                    p[0] == param_name
                    for p in parameters
                ):
                    raise LangError(
                        "Duplicate parameter: "
                        + param_name
                    )

                parameters.append(
                    (param_name, default)
                )

            functions[function_name] = (
                parameters,
                lines[i + 1:end],
            )

            i = end + 1
            continue

        # ====================================
        # CONTROL FLOW
        # ====================================

        if line == "break":
            raise BreakSignal()

        if line == "continue":
            raise ContinueSignal()

        if line == "return":
            raise ReturnSignal(None)

        if line.startswith("return "):
            raise ReturnSignal(
                value_of(line[7:])
            )

        # ====================================
        # PRINT / SAY
        # ====================================

        if line.startswith(("print ", "say ")):
            expression = (
                line[6:].strip()
                if line.startswith("print ")
                else line[4:].strip()
            )

            try:
                print(display(value_of(expression)))
            except LangError:
                if (
                    re.fullmatch(
                        r"[A-Za-z_][A-Za-z0-9_ ]*"
                        r"[!?.,]*",
                        expression
                    )
                    and not expression.isidentifier()
                ):
                    print(expression)
                else:
                    raise

            i += 1
            continue

        # ====================================
        # WAIT
        # ====================================

        if line.startswith("wait "):
            sleep(value_of(line[5:]))
            i += 1
            continue

        # ====================================
        # SYSTEM STATEMENT
        # ====================================

        if line.startswith("system "):
            command = value_of(line[7:])
            system(command)
            i += 1
            continue

        # ====================================
        # DEBUG
        # ====================================

        if line == "debug":
            print("=== VARIABLES ===")

            for name, value in variables.items():
                print(
                    f"{name} ({types.get(name, 'any')})"
                    f" = {value!r}"
                )

            print("=== FUNCTIONS ===")
            print(", ".join(functions) or "(none)")

            i += 1
            continue

        # ====================================
        # VARIABLE DECLARATION
        # ====================================

        match = re.fullmatch(
            r"(list<[^>]+>|int|float|string|text|bool|any)"
            r"\s+([A-Za-z_]\w*)\s*=\s*(.+)",
            line,
            re.S
        )

        if match:
            spec, name, expression = match.groups()

            assign(
                name,
                value_of(expression),
                spec
            )

            i += 1
            continue

        # ====================================
        # LIST / DICTIONARY ASSIGNMENT
        # ====================================

        match = re.fullmatch(
            r"([A-Za-z_]\w*)\s*\[(.+)\]"
            r"\s*=\s*(.+)",
            line,
            re.S
        )

        if match:
            name, key_expr, value_expr = match.groups()

            if name not in variables:
                raise LangError(
                    f"Unknown variable: {name}"
                )

            obj = variables[name]
            key = value_of(key_expr)
            value = value_of(value_expr)
            spec = types.get(name, "any")

            if spec.startswith("list<"):
                parts = split_top(spec[5:-1])

                if len(parts) == 1:
                    if (
                        not isinstance(obj, list)
                        or type(key) is not int
                        or not check(value, parts[0])
                    ):
                        raise LangError(
                            "Invalid list assignment"
                        )

                elif len(parts) == 2:
                    if (
                        not isinstance(obj, dict)
                        or not check(key, parts[0])
                        or not check(value, parts[1])
                    ):
                        raise LangError(
                            "Invalid dictionary assignment"
                        )

            if not isinstance(obj, (list, dict)):
                raise LangError(
                    f"{name} is not a collection"
                )

            obj[key] = value

            i += 1
            continue

        # ====================================
        # VARIABLE REASSIGNMENT
        # ====================================

        match = re.fullmatch(
            r"([A-Za-z_]\w*)\s*=\s*(.+)",
            line,
            re.S
        )

        if match:
            name, expression = match.groups()

            assign(
                name,
                value_of(expression)
            )

            i += 1
            continue

        # ====================================
        # STANDALONE FUNCTION CALL
        # ====================================

        if re.match(
            r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\s*\(",
            line
        ):
            evaluate(line)
            i += 1
            continue

        raise LangError(
            f"Unknown statement: {line}"
        )


# ============================================
# PROGRAM ENTRY POINT
# ============================================

def main():
    if len(sys.argv) != 2:
        sys.exit(
            "Usage: python main.py program.txt"
        )

    filename = sys.argv[1]

    try:
        source = Path(filename).read_text(
            encoding="utf-8"
        )

        lines = logical_lines(source)
        execute(lines)

    except ReturnSignal:
        sys.exit(
            "Language error: return outside a function"
        )

    except BreakSignal:
        sys.exit(
            "Language error: break outside a loop"
        )

    except ContinueSignal:
        sys.exit(
            "Language error: continue outside a loop"
        )

    except LangError as error:
        sys.exit(
            f"Language error: {error}"
        )

    except (
        ValueError,
        TypeError,
        KeyError,
        IndexError,
        ZeroDivisionError,
        OverflowError,
        SyntaxError,
        OSError,
        AttributeError,
        RecursionError,
    ) as error:
        sys.exit(
            f"Language error: {error}"
        )



# OPARIALANG_NATIVE_COMPILER
def native_compile_cli():
    if len(sys.argv) >= 3 and sys.argv[1] == "compile":
        from compiler import compile_oparia
        output = None

        if "-o" in sys.argv:
            index = sys.argv.index("-o")
            if index + 1 >= len(sys.argv):
                raise SystemExit("Missing output filename")
            output = sys.argv[index + 1]

        compile_oparia(sys.argv[2], output)
        return True

    return False


if __name__ == "__main__":
    if not native_compile_cli():
        main()
