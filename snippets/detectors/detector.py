from snippets.detectors.detect_python import detect_python_snippets
from snippets.detectors.detect_javascript import detect_javascript_snippets
from snippets.detectors.detect_java import detect_java_snippets
from snippets.detectors.detect_cpp import detect_cpp_snippets
from snippets.detectors.detect_html import detect_html_snippets

def detect_snippets(code: str, lang: str) -> list:
    if lang == 'python':
        return detect_python_snippets(code)
    elif lang == 'javascript':
        return detect_javascript_snippets(code)
    elif lang == 'java':
        return detect_java_snippets(code)
    elif lang == 'cpp':
        return detect_cpp_snippets(code)
    elif lang == 'html':
        return detect_html_snippets(code)
    else:
        return []