import re

def detect_html_snippets(code: str) -> list:
    snippets = []
    tags_to_detect = ['<head>', '<body>', '<script>', '<form>', '<nav>', '<header>', '<footer>', '<ul>', '<ol>', '<table>']

    for tag in tags_to_detect:
        start = 0
        closing_tag = tag.replace('<', '</')
        regex = f'<{tag[1:-1]}\\b[^>]*>|{closing_tag}'
        tags = re.finditer(regex, code, re.IGNORECASE)
        stack = list(map(lambda t: (t.group(), t.start(), t.end()), tags))
        while start < len(stack):
            if stack[start][0].lower() == tag:
                depth = 1
                for i in range(start + 1, len(stack)):
                    if stack[i][0].lower() == tag:
                        depth += 1
                    elif stack[i][0].lower() == closing_tag:
                        depth -= 1
                    if depth == 0:
                        snippets.append(code[stack[start][1]:stack[i][2]])
                        start = i
                        break
            start += 1

    return snippets

""" print(detect_html_snippets(

    '''
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <script>
        console.log('Hello, world!');
        function test() {
            alert('Nested script!');
        }
    </script>
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a href="#">Home</a></li>
                <li><a href="#">About</a></li>
            </ul>
        </nav>
    </header>
    
    <form action="/submit" method="post">
        <input type="text" name="username">
        <input type="submit" value="Submit">
    </form>

    <footer>
        <p>© 2025 Example</p>
    </footer>
</body>
</html>
'''
)) """