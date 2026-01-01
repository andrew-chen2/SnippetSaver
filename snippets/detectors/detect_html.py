import re

def detect_html_snippets(code: str) -> list:
    snippets = []
    tags = ['<head>', '<body>', '<script>', '<form>', '<nav>', '<header>', '<footer>', '<ul>', '<ol>', '<table>', '<style>', '<div>']

    for tag in tags:
        start = 0
        closing_tag = tag.replace('<', '</')
        regex = f'<{tag[1:-1]}\\b[^>]*>|{closing_tag}'
        tags = re.finditer(regex, code, re.IGNORECASE)
        stack = list(map(lambda t: (t.group(), t.start(), t.end()), tags))
        while start < len(stack):
            if re.match(f'<{tag[1:-1]}\\b[^>]*>', stack[start][0], re.IGNORECASE):
                depth = 1
                for i in range(start + 1, len(stack)):
                    if stack[i][0].lower() == closing_tag:
                        depth -= 1
                    else:
                        depth += 1
                    if depth == 0:
                        snippet = code[stack[start][1]:stack[i][2]]
                        if len(snippet.strip()) > 10000 or snippet.count('\n') < 1:
                            break
                        snippets.append(snippet)
                        start = i
                        break
            start += 1

    return snippets