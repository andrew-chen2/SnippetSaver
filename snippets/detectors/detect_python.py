import ast

def detect_python_snippets(code: str) -> list:
    snippets = []
    tree = ast.parse(code)
    nodes = ast.walk(tree)
    for node in nodes:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.For, ast.While, ast.Match)):
            snippet = ast.get_source_segment(code, node)
            if len(snippet.strip()) > 10000 or snippet.count('\n') < 1:
                continue
            snippets.append(snippet)

    return snippets

