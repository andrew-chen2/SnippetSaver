import re # Import the regex module

def detect_curly_brace_snippets(code: str, keywords: list) -> list:
    snippets = [] # Initialise empty list to store snippets

    # Iterate through keywords
    for keyword in keywords:
        regex = f'\\b{keyword}\\b' # Regex to find instances of the keyword
        matches = re.finditer(regex, code) # Find all matches in the code
        # Iterate through matches
        for match in matches:
            start = 0
            braces = re.finditer('{|}', code[match.end():]) # Find all curly braces after the match
            # Convert match objects to list of tuples
            stack = list(map(lambda b: (b.group(), b.start(), b.end()), braces))
            found = False # Flag to indicate if the snippet is found
            while start < len(stack):
                if found:
                    break # Break if snippet is already found
                if stack[start][0] == '{': # Check for opening brace
                    depth = 1
                    # Iterate through remaining braces to find matching closing brace
                    for i in range(start + 1, len(stack)):
                        # Increment or decrement depth based on brace type
                        if stack[i][0] == '}':
                            depth -= 1
                        else:
                            depth += 1
                        # Zero depth means matching closing brace found
                        if depth == 0:
                            # Extract snippet from keyword to closing brace
                            snippet = code[match.start():match.end()+stack[i][2]]
                            # Ignore snippets that are too long or too short
                            if len(snippet.strip()) > 10000 or snippet.count('\n') < 1:
                                found = True # Set found flag to true so it doesn't try to find more
                                break # Break out of the for loop
                            snippets.append(snippet) # Add snippet to list
                            found = True # Set found flag to true so it doesn't try to find more
                            break # Break out of the for loop
                start += 1 # Move to the next brace

    return snippets # Return the list of detected snippets