class Filter:
    def __init__(self, get_db):
        self.get_db = get_db
        self.user_id = None
        self.sort = None
        self.sort_order = None
        self.search = None
        self.max_dist = 3

    def set_sort(self, sort: str, order: str):
        self.sort = sort
        self.order = order

    def clear_sort(self):
        self.sort = None
        self.order = None

    def set_search(self, search: str):
        self.search = search

    def clear_search(self):
        self.search = None

    def get_results(self):
        con = self.get_db()

        # Get all snippets and order
        sql = "SELECT * FROM snippets WHERE user_id = ? ORDERBY ? ?"
        cur = con.execute(sql, (self.user_id, self.sort, self.order))
        snippets =  cur.fetchall()

        if not self.search:
            return snippets
        
        # Apply search with Levenshtein distance
        return snippets
