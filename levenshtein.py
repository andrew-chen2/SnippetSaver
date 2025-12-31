def levenshtein_dist(str1: str, str2: str) -> int:
    # Get lengths of the strings
    len1 = len(str1) + 1
    len2 = len(str2) + 1

    if len1 == 1 or len2 == 1:
        # At least one string is empty so distance is the length of the other
        return len2 - 1 or len1 - 1
    
    # Initialize distance matrix
    dist = [[0 for _ in range(len2)] for _ in range(len1)]

    # Fill first row and column
    for i in range(len1):
        dist[i][0] = i

    for i in range(len2):
        dist[0][i] = i

    for i in range(1, len1):
        for j in range(1, len2):
            if str1[i-1] == str2[j-1]:
                # Characters are the same so no cost
                dist[i][j] = dist[i-1][j-1]
            else:
                # Characters don't match so get minimum of insertion, deletion, substitution
                dist[i][j] = 1 + min(
                    dist[i][j-1],
                    dist[i-1][j],
                    dist[i-1][j-1]
                )
    # Bottom-right cell contains the Levenshtein distance
    return dist[len1-1][len2-1]

def fuzzy_search(haystack: str, needle: str) -> bool:
    THRESHOLD = 0.3
    haystack_len = len(haystack)
    needle_len = len(needle)

    if needle in haystack:
        return True

    # Only do fuzzy search for needles longer than 3 characters
    if needle_len < 4:
        return needle in haystack
    
    for i in range(haystack_len - needle_len + 1):
        sub_str = haystack[i:i+needle_len]

        if levenshtein_dist(sub_str, needle) / len(needle) <= THRESHOLD:
            return True
        
    return False