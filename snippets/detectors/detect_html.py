from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter

formatter = HTMLFormatter(indent=4)

def detect_html_snippets(code: str) -> list:
    snippets = [] # Initialise empty list to store snippets
    # List of HTML tags to search for
    tags = ['head', 'body', 'script', 'form', 'nav', 'header', 'footer', 'ul', 'ol', 'table', 'style', 'div']

    soup = BeautifulSoup(code, 'html.parser') # Parse the code

    # Iterate through tags
    for tag in tags:
        elements = soup.find_all(tag) # Find all elements with the current tag
        # Iterate through elements
        for element in elements:
            if element.parent.name == element.name and not element.find_next_sibling() and not element.find_previous_sibling():
                continue  # Skip if the parent is the same tag and no siblings
            snippet = element.prettify(formatter=formatter).strip('\n') # Convert Tag object to string
            # Ignore snippets that are too long or too short
            if len(snippet.strip()) > 10000 or snippet.count('\n') < 1:
                continue
            snippets.append(snippet) # Add snippet to list
    
    return snippets # Return the list of detected snippets