# Language Syntax Reference

Complete syntax reference for the custom programming language implemented in `main.py`, including its optional `lang_extensions.py` features.

## 1. Hello World

```text
print "Hello, World!"
```

Alternatively:

```text
say "Hello, World!"
```

Programs are stored in text files, such as `program.txt`, and executed by the Python-based interpreter.

## 2. Variables and Data Types

Variables are declared using:

`type name = value`

```text
int age = 10
float pi = 3.14159
string name = "Samwise"
text greeting = "Hello"
bool active = true
any something = 123
```

Supported types:

| Type | Description |
|---|---|
| `int` | Integer numbers |
| `float` | Decimal numbers |
| `string` | Text |
| `text` | Alias for `string` |
| `bool` | Boolean values |
| `any` | Any supported value |
| `list<T>` | Typed lists |
| `list<K,V>` | Typed dictionaries |
| `null` | Null value literal |

### Changing variables

```text
int score = 10
score = 20
score = score + 5
```

A variable's new value must match its declared type.

Variables must be declared before normal reassignment.

## 3. Strings

```text
string greeting = "Hello"
string name = "World"

print greeting + " " + name
```

### Escape sequences

```text
print "Hello\nWorld"
print "Column1\tColumn2"
print "She said \"Hello\""
print "C:\\Users\\Samwise"
```

| Escape | Meaning |
|---|---|
| `\n` | New line |
| `\t` | Tab |
| `\"` | Double quotation mark |
| `\\` | Backslash |
| `\'` | Single quotation mark |

### F-strings

F-strings interpolate variables and expressions.

```text
string a = "Hello"

print f"#{a}\n"
print f"Value: {10 + 5}"
```

More examples:

```text
int age = 10
string name = "Samwise"

print f"Hello {name}!"
print f"You are {age} years old"
print f"Next year: {age + 1}"
```

Formatting is supported through Python's f-string expression evaluator.

```text
float pi = 3.14159265

print f"Pi: {pi:.2f}"
```

Ordinary strings do not interpolate variables automatically.

## 4. Arithmetic

```text
print 10 + 5
print 10 - 5
print 10 * 5
print 10 / 5
print 10 // 3
print 10 % 3
print 2 ** 8
```

| Operator | Meaning |
|---|---|
| `+` | Addition / string concatenation |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `//` | Floor division |
| `%` | Modulo |
| `**` | Exponentiation |

Parentheses are supported.

```text
print (10 + 5) * 2
```

## 5. Comparisons and Boolean Logic

```text
print 10 == 10
print 10 != 5
print 10 > 5
print 10 < 20
print 10 >= 10
print 5 <= 10
```

Boolean operators:

```text
print true and false
print true or false
print not false
```

Membership checks:

```text
print 2 in [1, 2, 3]
print 5 not in [1, 2, 3]
```

Identity comparisons are also supported:

```text
print null is null
print 10 is not null
```

## 6. Printing

```text
print "Hello"
print 123
print true
print 10 + 20
```

The `say` keyword behaves like `print`.

```text
say "Hello!"
say 100
say f"Result: {10 + 20}"
```

Boolean output appears as `true` or `false`. Null output appears as `null`.

Simple unquoted text containing spaces can also be printed.

```text
say Hello World
```

Use quotes for reliable handling of punctuation and expressions.

## 7. User Input

```text
string name = input("Enter your name: ")
print name
```

Convert input to another type:

```text
int age = int(input("Age: "))
float height = float(input("Height: "))
```

`input()` returns a string before conversion.

## 8. Lists

Create a typed list:

```text
list<string> names = {"Alice", "Bob", "Charlie"}
list<int> numbers = {10, 20, 30}
```

Multiline declarations:

```text
list<string> fruits = {
    "Apple",
    "Banana",
    "Orange"
}
```

Access elements:

```text
print fruits[0]
print fruits[1]
```

Modify elements:

```text
fruits[0] = "Mango"
```

List indexing begins at zero.

### List slicing

```text
list<int> numbers = {10, 20, 30, 40, 50}

print numbers[1:3]
print numbers[:3]
print numbers[2:]
```

## 9. Dictionaries

Use `list<keyType, valueType>`:

```text
list<string,int> scores = {
    "Alice": 100,
    "Bob": 95,
    "Charlie": 80
}
```

Read and update values:

```text
print scores["Alice"]

scores["Bob"] = 99
```

Mixed key types can use `any`:

```text
list<any,string> messages = {
    100: "Success",
    "error": "Something failed"
}
```

### Dictionary functions

```text
print keys(scores)
print values(scores)
print items(scores)
```

## 10. If / Elsif / Else

```text
int age = 15

if age >= 18 {
    print "Adult"
} elsif age >= 13 {
    print "Teenager"
} else {
    print "Child"
}
```

Simple condition:

```text
if true {
    print "This executes"
}
```

Conditions can be nested:

```text
if age > 10 {
    if age < 20 {
        print "Between 10 and 20"
    }
}
```

The language uses `elsif`, not `elif`.

## 11. While Loops

```text
int i = 0

while i < 5 {
    print i
    i = i + 1
}
```

The interpreter limits a while loop to 1,000,000 iterations.

## 12. Repeat Loops

```text
repeat 5 {
    print "Hello"
}
```

The repeat count must be an integer from 0 to 1,000,000.

The current iteration index is assigned to `i`, starting at zero.

```text
repeat 5 {
    print i
}
```

## 13. For Loops

```text
list<string> names = {"Alice", "Bob", "Charlie"}

for name in names {
    print name
}
```

Using `range()`:

```text
for i in range(10) {
    print i
}
```

Using a range with start and stop values:

```text
for i in range(5, 15) {
    print i
}
```

## 14. Break and Continue

`break` exits the current loop.

```text
int i = 0

while i < 100 {
    if i == 5 {
        break
    }

    print i
    i = i + 1
}
```

`continue` skips to the next iteration.

```text
for i in range(10) {
    if i == 5 {
        continue
    }

    print i
}
```

## 15. Functions

Functions begin with `func`.

```text
func hello() {
    print "Hello!"
}

hello()
```

### Parameters

```text
func greet(name) {
    print "Hello, " + name
}

greet("Samwise")
```

### Return values

```text
func add(a, b) {
    return a + b
}

print add(5, 10)
```

### Default arguments

```text
func greet(name = "World") {
    print "Hello, " + name
}

greet()
greet("Alice")
```

### Named arguments

```text
func multiply(a, b) {
    return a * b
}

print multiply(a = 10, b = 5)
```

Positional and named arguments can be combined.

```text
print multiply(10, b = 5)
```

### Global variables

Functions can modify existing global variables.

```text
int score = 0

func addScore(points) {
    score = score + points
}

addScore(50)

print score
```

Function parameters temporarily shadow global variables with matching names and are restored after the function returns. Other variables use shared storage.

## 16. Built-in Functions

| Function | Description |
|---|---|
| `input()` | Read user input |
| `len()` | Get length |
| `str()` | Convert to string |
| `int()` | Convert to integer |
| `float()` | Convert to float |
| `bool()` | Convert to boolean |
| `range()` | Generate integer sequence |
| `abs()` | Absolute value |
| `min()` | Minimum |
| `max()` | Maximum |
| `sum()` | Sum numbers |
| `round()` | Round numbers |
| `upper()` | Uppercase text |
| `lower()` | Lowercase text |
| `strip()` | Trim whitespace |
| `replace()` | Replace text |
| `split()` | Split a string |
| `join()` | Join values |
| `contains()` | Membership test |
| `keys()` | Dictionary keys |
| `values()` | Dictionary values |
| `items()` | Dictionary entries |
| `list()` | Create/convert a list |
| `dict()` | Create/convert a dictionary |
| `wait()` | Pause execution |
| `sleep()` | Pause execution |
| `system()` | Execute a shell command |

Examples:

```text
print len("Hello")
print upper("hello")
print lower("HELLO")
print abs(-15)
print round(3.14159, 2)
print contains([1, 2, 3], 2)
```

## 17. File Operations

File operations use the `File` namespace.

### File.write()

Create or overwrite a file.

```text
File.write("hello.txt", "Hello World!")
```

Writing a variable:

```text
string message = "Hello from my language!"

File.write("message.txt", message)
```

Writing newlines:

```text
File.write("notes.txt", "Line 1\nLine 2\n")
```

### File.append()

Append content without removing existing contents.

```text
File.append("hello.txt", "\nAnother line!")
```

### File.read()

Read an entire text file.

```text
string content = File.read("hello.txt")

print content
```

### File.exists()

Check whether a file or directory exists.

```text
bool exists = File.exists("hello.txt")

print exists
```

### File.delete()

Delete a file.

```text
File.delete("old.txt")
```

### File.mkdir()

Create a directory, including missing parents.

```text
File.mkdir("projects/myproject")
```

### File.size()

Read file size in bytes.

```text
int size = File.size("hello.txt")

print size
```

### File API summary

| Function | Purpose |
|---|---|
| `File.write(path, text)` | Write/overwrite a file |
| `File.append(path, text)` | Append text |
| `File.read(path)` | Read text |
| `File.exists(path)` | Check path existence |
| `File.delete(path)` | Delete a file |
| `File.mkdir(path)` | Create directories |
| `File.size(path)` | Get file size in bytes |

## 18. System Commands

The `system()` function executes operating-system shell commands.

### Basic syntax

```text
system("echo Hello World")
```

### Linux commands

```text
system("pwd")
system("ls")
system("ls -la")
system("whoami")
system("uname -a")
```

### Run Python

```text
system("python --version")
```

### Run a shell script

```text
system("bash script.sh")
```

### Execute with a variable

```text
string command = "echo Hello from my language!"

system(command)
```

### Return exit code

`system()` returns the command's numeric exit code by default.

```text
int result = system("echo Hello")

print result
```

An exit code of `0` conventionally indicates success.

### Capture command output

The second argument enables output capture.

```text
string output = system("pwd", true)

print output
```

When capture is enabled, standard output is returned as a string instead of being printed directly.

### Check execution status

The third argument makes nonzero exit codes raise a language error.

```text
system("echo Checking", false, true)
```

### Alternative statement syntax

```text
system "echo Hello"
```

The interpreter also accepts `system` followed by an expression as a statement.

**Warning:** Commands execute through the system shell with the permissions of the current user. Only execute trusted commands and avoid constructing commands from untrusted input.

## 19. External Python Code

Use `extern "Python"` to execute Python code.

### Syntax

```text
extern "Python" {
print("Hello from Python!")
}
```

Python code executes in the same Python process as the language interpreter.

### Python calculations

```text
extern "Python" {
import math

print(math.sqrt(144))
print(math.pi)
}
```

### Access language variables

```text
int score = 100

extern "Python" {
print(score)
score = score + 50
}

print score
```

Result:

```text
100
150
```

### Create variables from Python

```text
extern "Python" {
message = "Created in Python"
number = 42
}

print message
print number
```

### Python functions

```text
extern "Python" {
def hello(name):
    return "Hello " + name

print(hello("Samwise"))
}
```

Python functions exported as variables can also be called as language expressions.

```text
extern "Python" {
def multiply(a, b):
    return a * b
}

print multiply(5, 10)
```

### Python modules

Python's normal installed modules can be imported.

```text
extern "Python" {
import random

print(random.randint(1, 100))
}
```

**Important:** External Python code has access to Python's built-ins and runs with the interpreter's privileges. Python variable updates are checked against existing declared language types when exported.

## 20. External C Code

Use `extern "C"` to compile and execute C code.

### Syntax

```text
extern "C" {
printf("Hello from C!\n");
}
```

When the source does not contain a `main()` function, the interpreter automatically provides a minimal C program with common headers and an entry point.

### C arithmetic

```text
extern "C" {
int a = 10;
int b = 20;

printf("Result: %d\n", a + b);
}
```

### C loops

```text
extern "C" {
for (int i = 0; i < 5; i++) {
    printf("%d\n", i);
}
}
```

### Full C program

You can also supply a full program with your own `main()`.

```text
extern "C" {
#include <stdio.h>

int main(void) {
    printf("Hello from a full C program!\n");
    return 0;
}
}
```

The interpreter uses `gcc` to compile the C source into a temporary executable, runs the executable, and cleans up the temporary files.

C uses its native syntax inside the external block, not the custom language's syntax.

**Limitations:** C code executes in a separate process and does not directly share custom-language variables. Native program output is forwarded to the terminal. The current implementation is not a callable C foreign-function interface.

## 21. External C++ Code

Use `extern "C++"` to compile and execute C++ code.

### Syntax

```text
extern "C++" {
cout << "Hello from C++!" << endl;
}
```

### C++ variables

```text
extern "C++" {
int age = 10;
string name = "Samwise";

cout << name << " is " << age << endl;
}
```

### C++ loops

```text
extern "C++" {
for (int i = 0; i < 10; i++) {
    cout << i << endl;
}
}
```

### C++ vectors

```text
extern "C++" {
vector<int> numbers = {10, 20, 30};

for (int number : numbers) {
    cout << number << endl;
}
}
```

### Full C++ program

```text
extern "C++" {
#include <iostream>
using namespace std;

int main() {
    cout << "Full C++ program!" << endl;
    return 0;
}
}
```

C++ code is compiled using `g++`.

If no `main()` is supplied, the interpreter automatically generates one and supplies common standard-library headers.

### Language aliases

The interpreter also recognizes:

```text
extern "cpp" {
cout << "Hello!" << endl;
}
```

**Limitations:** Like C, the C++ block runs in a separate process. C++ variables and functions are not automatically imported into the custom-language environment.

## 22. Combining Python, C, C++, and System Commands

You can use all four execution mechanisms in one program.

```text
say "Starting multilingual program!"

system("echo Running Linux shell")

extern "Python" {
print("Python is running!")
}

extern "C" {
printf("C is running!\n");
}

extern "C++" {
cout << "C++ is running!" << endl;
}

say "All languages finished!"
```

### Execution model

| Feature | Execution method |
|---|---|
| Custom language | Python interpreter |
| `system()` | Operating-system shell |
| `extern "Python"` | Python `exec()` |
| `extern "C"` | GCC compilation and executable |
| `extern "C++"` | G++ compilation and executable |

External C and C++ blocks require their respective compilers. They do not create persistent, automatically callable native functions.

External blocks execute when the interpreter encounters them, including inside a function or loop.

## 23. Waiting and Sleeping

You can pause the program with the `wait` statement.

```text
wait 1
```

Or call the built-in functions:

```text
wait(1)
sleep(0.5)
```

The maximum supported delay per call is 86,400 seconds.

Example:

```text
repeat 5 {
    print i
    wait 1
}
```

## 24. GUI Programming

The interpreter can expose GUI operations through the optional `lang_extensions.py` module.

When that module is installed and defines `gui`, the interpreter makes it accessible as:

```text
gui
```

The intended API includes GUI operations such as:

- Window creation and configuration
- Window titles and sizes
- Labels and buttons
- Inputs and other controls
- Layout and containers
- Widget methods and event handling

For example, the requested API names include:

```text
gui.title(...)
gui.label(...)
gui.button(...)
```

The exact argument signatures, widget methods, and event loop depend on the installed `lang_extensions.py` implementation.

### GTK4 support

GTK4 integration belongs to the GUI extension, rather than the language interpreter's core syntax.

The interpreter forwards supported calls to the extension. GTK4 itself must be installed and correctly configured for that extension.

The `gui` object is only available when the optional module exposes it.

## 25. Namespaces

The optional extensions module can expose a `namespace` callable.

Namespaces are intended to organize related values and functionality under a single name.

The extension entry point is:

```text
namespace(...)
```

The exact constructor arguments and how members are registered depend on `lang_extensions.py`.

The expression evaluator supports selected public attribute access for the extension's namespace objects.

General Python-style attribute access on arbitrary objects is not supported.

## 26. Classes

The optional `lang_extensions.py` module can provide the class-creation API:

```text
create_class(...)
```

This is an extension-backed feature, separate from user-defined language functions.

Class creation, object construction, attributes, and methods are controlled by the extension.

The core interpreter does not currently parse native class declarations such as:

```text
class Person {
}
```

That syntax requires additional parser and runtime support.

## 27. Local Libraries

The optional extension module can expose:

```text
load_library(...)
```

This is intended to load local libraries into the programming environment.

Library loading behavior, supported file formats, search paths, and exports are defined by `lang_extensions.py`.

This is different from the external-language execution mechanism.

For example, `extern "Python"` immediately executes a Python block, while `load_library()` delegates library loading to the extension.

## 28. Comments

```text
# This is a comment

// This is another comment

print "Hello"
```

Comments must occupy their own lines in the current interpreter.

Inline comments are not reliably supported.

## 29. Debugging

The interpreter provides a `debug` statement.

```text
int score = 100
string name = "Samwise"

debug
```

It displays information about declared variables, their types, current values, and registered user functions.

For programs that use extensions, this may also show extension objects registered in global storage.

## 30. Error Handling

The interpreter reports language errors for invalid operations.

### Type mismatch

```text
int age = "Hello"
```

### Unknown variable

```text
print unknownVariable
```

### Duplicate declaration

```text
int x = 10
int x = 20
```

### Unknown function

```text
unknownFunction()
```

### External compilation error

Invalid C or C++ source can produce a compiler error containing the compiler's diagnostic output.

### Shell command failure

By default, `system()` returns the command exit code.

To turn a nonzero exit code into a language error, use:

```text
system("false", false, true)
```

There is no user-level `try` / `catch` syntax yet.

## 31. Complete Multilingual Program

The following example combines language variables, functions, loops, Python execution, C execution, C++ execution, shell commands, and file operations.

```text
# Multilingual example

string username = input("Your name: ")
int score = 0

say f"Welcome, {username}!"

func addPoints(points = 10) {
    score = score + points
}

repeat 5 {
    addPoints()
}

say f"Your score is {score}"

list<string> achievements = {
    "Beginner",
    "Builder",
    "Programmer"
}

for achievement in achievements {
    print achievement
}

if score >= 50 {
    say "Congratulations!"
} else {
    say "Keep playing!"
}

# Write a file
File.write("results.txt", f"User: {username}\nScore: {score}\n")

# Run a Linux command
system("echo System command completed")

# Run Python
extern "Python" {
import math

print("Python square root:", math.sqrt(144))
}

# Run C
extern "C" {
int a = 10;
int b = 20;

printf("C result: %d\n", a + b);
}

# Run C++
extern "C++" {
vector<int> numbers = {1, 2, 3, 4, 5};

for (int number : numbers) {
    cout << "C++ number: " << number << endl;
}
}

say "Reading results file:"
say File.read("results.txt")

say "Program finished!"
```

## 32. Syntax Limitations

The current interpreter has several limitations:

- Native class declarations are not implemented in the core parser.
- Module imports using a custom `import` statement are not implemented.
- Function parameters are temporary bindings, but other variables use global storage.
- Compound assignments such as `+=` and `-=` are not supported.
- `try` / `catch` statements are not supported.
- Arbitrary object-method calls are restricted.
- Inline comments are not reliably supported.
- General multiline expressions are not fully supported.
- The current external-block parser expects the external block's closing delimiter to be a standalone `}` line. A nested native-language closing brace on a standalone line can be mistaken for the end of the external block; the simple examples above keep nested closing braces on lines such as `} else {` or use a full source structure where this remains a parser limitation.
- External C and C++ blocks are compiled and executed independently.
- Native functions are not automatically exposed to the language.
- GUI, namespace, class-creation, and local-library functionality depends on `lang_extensions.py`.
- Arbitrary shell commands and external code are not sandboxed.

## 33. Feature Summary

| Feature | Status |
|---|---|
| Variables and typed declarations | Supported |
| Strings and f-strings | Supported |
| Arithmetic and comparisons | Supported |
| Lists and dictionaries | Supported |
| If / elsif / else | Supported |
| While / repeat / for | Supported |
| Break and continue | Supported |
| Functions and arguments | Supported |
| Global variable updates | Supported |
| Input and output | Supported |
| File operations | Supported |
| System shell commands | Supported |
| External Python execution | Supported |
| External C compilation and execution | Supported |
| External C++ compilation and execution | Supported |
| Wait and sleep | Supported |
| Debug statement | Supported |
| GUI via extension | Conditional |
| Namespaces via extension | Conditional |
| Classes via extension | Conditional |
| Local libraries via extension | Conditional |
| Native callable C/C++ FFI | Not implemented |
| Custom module imports | Not implemented |
| Try / catch | Not implemented |
| Isolated local variable scopes | Not implemented |

---

**End of Language Syntax Reference**