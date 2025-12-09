def levenshtein_dist(str1: str, str2: str) -> int:
    m = len(str1)
    n = len(str2)

    if m == 0 or n == 0:
        return n or m

    dp = [[0 for _ in range(n+1)] for _ in range(m+1)]

    for i in range(m+1):
        dp[i][0] = i
    
    for i in range(n+1):
        dp[0][i] = i

    for i in range(1, m+1):
        for j in range(1, n+1):
            if str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i][j-1],
                    dp[i-1][j],
                    dp[i-1][j-1]
                )
    return dp[m][n]

def fuzzy_search(haystack: str, needle: str, max_dist: int) -> bool:
    haystack_len = len(haystack)
    needle_len = len(needle)
    
    for i in range(haystack_len - needle_len + 1):
        sub_str = haystack[i:i+needle_len]

        if levenshtein_dist(sub_str, needle) <= max_dist:
            return True
        
    return False