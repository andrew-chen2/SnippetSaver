import datetime
import uuid

class Snippet:
    def __init__(self, get_db, user_id, snippet_id = None):
        self.get_db = get_db
        self.user_id = user_id
        self.snippet_id = snippet_id
        if snippet_id:
            con = self.get_db()
            sql = "SELECT * FROM snippets WHERE id = ? AND user_id = ?"
            cur = con.execute(sql, (snippet_id, user_id))
            snippet = cur.fetchone()
            if not snippet:
                raise ValueError("Snippet not found or access denied.")
            _, _,  self.title, self.code, self.language, self.share_id = snippet
            self.full_code = self.code  # When creating a new snippet full_code is the uploaded code and code is the selected portion
        else:
            self.title = ''
            self.full_code = ''
            self.code = ''
            self.language = None
            self.share_id = None

    def get_snippets_from_code(self) -> list:
        # Returns list of detected snippets as strings
        pass

    def save_snippet(self):
        con = self.get_db()

        # Validation
        if self.title.strip() == '':
            raise ValueError("Title cannot be empty.")
        if self.code.strip() == '':
            raise ValueError("Code cannot be empty.")

        # Store in database
        current_time = datetime.datetime.now()
        sql = "INSERT INTO snippets (user_id, title, code, language, created_at) VALUES (?, ?, ?, ?, ?)"
        con.execute(sql, (self.user_id, self.title, self.code, self.language, current_time))
        con.commit()
        self.snippet_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]

    def edit_snippet(self, new_title: str = None, new_code: str = None, new_language: str = None):
        con = self.get_db()

        # Validation
        if new_title.strip() == '':
            raise ValueError("Title cannot be empty.")
        if new_code.strip() == '':
            raise ValueError("Code cannot be empty.")

        # Update in database
        sql = "UPDATE snippets SET title = ?, code = ?, language = ? WHERE id = ? AND user_id = ?"
        con.execute(sql, (new_title, new_code, new_language, self.snippet_id, self.user_id))
        con.commit()

    def delete_snippet(self):
        con = self.get_db()
        sql = "DELETE FROM snippets WHERE id = ? AND user_id = ?"
        con.execute(sql, (self.snippet_id, self.user_id))
        con.commit()
        self.snippet_id = None

    def generate_share_id(self):
        if self.share_id:
            return self.share_id # Already has a share_id

        con = self.get_db()
        new_share_id = str(uuid.uuid4())
        sql = "UPDATE snippets SET share_id = ? WHERE id = ? AND user_id = ?"
        con.execute(sql, (new_share_id, self.snippet_id, self.user_id))
        con.commit()
        self.share_id = new_share_id

    def unshare(self):
        if not self.share_id:
            return 
        
        con = self.get_db()
        sql = "UPDATE snippets SET share_id = NULL WHERE id = ? AND user_id = ?"
        con.execute(sql, (self.snippet_id, self.user_id))
        con.commit()
        self.share_id = None