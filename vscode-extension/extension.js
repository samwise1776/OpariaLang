
const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

function locateInterpreter(document) {
    const cfg = vscode.workspace.getConfiguration('oparia');
    const specified = cfg.get('interpreterPath');

    if (specified) return specified;

    const folder = vscode.workspace.getWorkspaceFolder(document.uri);
    const bases = [];

    if (folder) bases.push(folder.uri.fsPath);
    bases.push(path.dirname(document.uri.fsPath));
    bases.push(path.resolve(__dirname, '..'));

    for (const base of bases) {
        const candidate = path.join(base, 'main.py');
        if (fs.existsSync(candidate)) return candidate;
    }

    return undefined;
}

function locatePython(interpreter, document) {
    const cfg = vscode.workspace.getConfiguration('oparia');
    const specified = cfg.get('pythonPath');

    if (specified) return specified;

    const folder = vscode.workspace.getWorkspaceFolder(document.uri);
    const bases = [];

    if (folder) bases.push(folder.uri.fsPath);
    if (interpreter) bases.push(path.dirname(interpreter));

    for (const base of bases) {
        const candidate = path.join(base, '.venv', 'bin', 'python');
        if (fs.existsSync(candidate)) return candidate;

        const windows = path.join(base, '.venv', 'Scripts', 'python.exe');
        if (fs.existsSync(windows)) return windows;
    }

    return process.platform === 'win32' ? 'python' : 'python3';
}

function diagnosticsFor(document) {
    const diagnostics = [];
    const lines = document.getText().split(/\r?\n/);

    const blocks = [];
    let external = false;

    const startsBlock = /^(?:if|elsif|else|while|repeat|for|func)\b.*\{\s*$/;
    const startsExtern = /^extern\s+["'](?:Python|C|C\+\+|cpp)["']\s*\{\s*$/i;

    for (let n = 0; n < lines.length; n++) {
        const raw = lines[n];
        const line = raw.trim();

        if (!line || line.startsWith('#') || line.startsWith('//')) {
            continue;
        }

        if (external) {
            if (line === '}') external = false;
            continue;
        }

        if (startsExtern.test(line)) {
            external = true;
            continue;
        }

        if (startsBlock.test(line)) {
            blocks.push(n);
            continue;
        }

        if (/^}\s*(?:elsif|else)\b.*\{\s*$/.test(line)) {
            continue;
        }

        if (line === '}') {
            if (blocks.length) {
                blocks.pop();
            } else {
                diagnostics.push(new vscode.Diagnostic(
                    new vscode.Range(n, 0, n, raw.length),
                    'Unexpected closing brace',
                    vscode.DiagnosticSeverity.Error
                ));
            }
        }
    }

    for (const n of blocks) {
        diagnostics.push(new vscode.Diagnostic(
            new vscode.Range(n, 0, n, lines[n].length),
            'Block may be missing a closing brace',
            vscode.DiagnosticSeverity.Warning
        ));
    }

    if (external) {
        diagnostics.push(new vscode.Diagnostic(
            new vscode.Range(lines.length - 1, 0, lines.length - 1, lines[lines.length - 1].length),
            'Unclosed external language block',
            vscode.DiagnosticSeverity.Warning
        ));
    }

    return diagnostics;
}

function activate(context) {
    const collection = vscode.languages.createDiagnosticCollection('oparia');
    context.subscriptions.push(collection);

    function update(document) {
        if (document.languageId !== 'oparia') return;

        if (!vscode.workspace.getConfiguration('oparia').get('diagnostics')) {
            collection.delete(document.uri);
            return;
        }

        collection.set(document.uri, diagnosticsFor(document));
    }

    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(update),
        vscode.workspace.onDidChangeTextDocument(e => update(e.document)),
        vscode.workspace.onDidCloseTextDocument(d => collection.delete(d.uri))
    );

    vscode.workspace.textDocuments.forEach(update);

    const run = vscode.commands.registerCommand('oparia.runFile', async () => {
        const editor = vscode.window.activeTextEditor;

        if (!editor || editor.document.languageId !== 'oparia') {
            vscode.window.showErrorMessage('Open an OpariaLang file first.');
            return;
        }

        await editor.document.save();

        const interpreter = locateInterpreter(editor.document);

        if (!interpreter) {
            vscode.window.showErrorMessage('OpariaLang main.py was not found.');
            return;
        }

        const python = locatePython(interpreter, editor.document);
        const terminal = vscode.window.createTerminal({
            name: 'OpariaLang',
            cwd: path.dirname(editor.document.uri.fsPath)
        });

        const quote = s => "'" + s.replace(/'/g, "'\\''") + "'";
        const command = process.platform === 'win32'
            ? `"${python}" "${interpreter}" "${editor.document.uri.fsPath}"`
            : `${quote(python)} ${quote(interpreter)} ${quote(editor.document.uri.fsPath)}`;

        terminal.show();
        terminal.sendText(command);
    });

    const newFile = vscode.commands.registerCommand('oparia.newFile', async () => {
        const doc = await vscode.workspace.openTextDocument({
            language: 'oparia',
            content: 'print "Hello from OpariaLang!"\n'
        });
        await vscode.window.showTextDocument(doc);
    });

    const snippetData = require('./snippets/oparia.json');
    const provider = vscode.languages.registerCompletionItemProvider(
        'oparia',
        {
            provideCompletionItems() {
                return Object.values(snippetData).map(item => {
                    const completion = new vscode.CompletionItem(
                        item.prefix,
                        vscode.CompletionItemKind.Snippet
                    );
                    completion.insertText = new vscode.SnippetString(
                        item.body.join('\n')
                    );
                    completion.detail = item.description;
                    return completion;
                });
            }
        },
        '.', '('
    );

    context.subscriptions.push(run, newFile, provider);
}

function deactivate() {}

module.exports = { activate, deactivate };
