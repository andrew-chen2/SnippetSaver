from snippets.detectors.curly_brace_langs import detect_curly_brace_snippets # Import the curly brace snippet detector

def detect_cpp_snippets(code: str) -> list:
    # Use the curly brace snippet detector with C++ keywords
    snippets = detect_curly_brace_snippets(code, ['void', 'class', 'for', 'while', 'switch'])
    return snippets # Return the detected snippets