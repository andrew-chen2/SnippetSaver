import re
from snippets.detectors.curly_brace_langs import detect_curly_brace_snippets

def detect_javascript_snippets(code: str) -> list:
    snippets = detect_curly_brace_snippets(code, ['function', 'class', 'for', 'while', 'switch', 'if', 'else'])
    return snippets