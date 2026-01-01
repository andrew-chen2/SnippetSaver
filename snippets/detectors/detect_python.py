import ast # Import the ast module for parsing Python code

def detect_python_snippets(code: str) -> list:
    snippets = [] # Initialise empty list to store snippets
    try:
        tree = ast.parse(code) # Parse the code into an abstract syntax tree
        nodes = ast.walk(tree) # Walk through nodes in the AST
        for node in nodes: # Iterate through nodes
            # Check for specific node types that indicate code blocks
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.For, ast.While, ast.Match)):
                snippet = ast.get_source_segment(code, node) # Get substring of the code for the node
                # Ignore snippets that are too long or too short
                if len(snippet.strip()) > 10000 or snippet.count('\n') < 1:
                    continue
                snippets.append(snippet) # Add snippet to list
    except Exception:
        pass # If parsing fails return empty list

    return snippets # Return the list of detected snippets