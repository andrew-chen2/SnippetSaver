import re # Import the regex module

def detect_html_snippets(code: str) -> list:
    snippets = [] # Initialise empty list to store snippets
    # List of HTML tags to search for
    tags = ['<head>', '<body>', '<script>', '<form>', '<nav>', '<header>', '<footer>', '<ul>', '<ol>', '<table>', '<style>', '<div>']

    # Iterate through tags
    for tag in tags:
        start = 0
        closing_tag = tag.replace('<', '</') # Get corresponding closing tag
        regex = f'<{tag[1:-1]}\\b[^>]*>|{closing_tag}' # Regex to find both opening and closing tags
        tags = re.finditer(regex, code, re.IGNORECASE) # Find all opening and closing tags in the code
        stack = list(map(lambda t: (t.group(), t.start(), t.end()), tags)) # Convert match objects to list of tuples
        while start < len(stack):
            # Check for opening tag
            if re.match(f'<{tag[1:-1]}\\b[^>]*>', stack[start][0], re.IGNORECASE):
                depth = 1
                # Iterate through remaining tags to find matching closing tag
                for i in range(start + 1, len(stack)):
                    # Increment or decrement depth based on tag type
                    if stack[i][0].lower() == closing_tag:
                        depth -= 1
                    else:
                        depth += 1
                    # Zero depth means matching closing tag found
                    if depth == 0:
                        # Extract snippet from opening to closing tag
                        snippet = code[stack[start][1]:stack[i][2]]
                        # Ignore snippets that are too long or too short
                        if len(snippet.strip()) > 10000 or snippet.count('\n') < 1:
                            break
                        snippets.append(snippet) # Add snippet to list
                        start = i # Restart from the position after the closing tag
                        break # Break out of the for loop
            start += 1 # Move to the next tag

    return snippets # Return the list of detected snippets