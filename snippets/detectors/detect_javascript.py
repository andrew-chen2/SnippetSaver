from snippets.detectors.curly_brace_langs import detect_curly_brace_snippets # Import the curly brace snippet detector

def detect_javascript_snippets(code: str) -> list:
    # Use the curly brace snippet detector with JavaScript keywords
    snippets = detect_curly_brace_snippets(code, ['function', 'class', 'for', 'while', 'switch', 'if', 'else'])
    return snippets # Return the detected snippets