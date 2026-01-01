import re
from snippets.detectors.curly_brace_langs import detect_curly_brace_snippets

def detect_cpp_snippets(code: str) -> list:
    snippets = detect_curly_brace_snippets(code, ['void', 'class', 'for', 'while', 'switch'])
    return snippets