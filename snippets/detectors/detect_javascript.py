import re

def detect_javascript_snippets(code: str) -> list:
    snippets = []
    keywords = ['function', 'class', 'async', 'for', 'while', 'switch']

    for keyword in keywords:
        regex = f'\\b{keyword}\\b'
        matches = re.finditer(regex, code)
        for match in matches:
            start = 0
            braces = re.finditer('{|}', code[match.start():])
            stack = list(map(lambda b: (b.group(), b.start(), b.end()), braces))
            found = False
            while start < len(stack):
                if found:
                    break
                if stack[start][0] == '{':
                    depth = 1
                    for i in range(start + 1, len(stack)):
                        if stack[i][0] == '}':
                            depth -= 1
                        else:
                            depth += 1
                        if depth == 0:
                            snippet = code[match.start():match.start()+stack[i][2]]
                            if len(snippet.strip()) > 10000 or snippet.count('\n') < 1:
                                found = True
                                break
                            snippets.append(snippet)
                            found = True
                            break
                start += 1

    return snippets