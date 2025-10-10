from levenshtein import fuzzy_search

order_params = [
    'modified_at', 
    'created_at', 
]

allowed_dirs = [
    'asc', 
    'desc',
]

allowed_langs = [
    'cpp', 
    'html', 
    'java', 
    'javascript', 
    'python',
]

MAX_DIST = 3

def get_snippets(get_db, search: str = '', order: str = 'modified_at', order_dir: str = 'desc', lang: str = None):
    if order not in order_params:
        raise ValueError("Order param not allowed.")
    if order_dir not in allowed_dirs:
        raise ValueError("Order direction not allowed.")
    if lang not in allowed_langs:
        raise ValueError("Language not allowed.")

    con = get_db()

    if lang:
        sql = f'SELECT * FROM snippets ORDER BY {order} {order_dir}'
    else:
        sql = f'SELECT * FROM snippets WHERE language = {lang} ORDER BY {order} {order_dir}'
    cur = con.execute(sql)
    snippets = cur.fetchall()

    if not search:
        return snippets

    return []