import datetime
import uuid

class Snippet:
    def __init__(self, get_db, user_id, title = None, code = None, language = None, snippet_id = None):
        self._get_db = get_db
        self.user_id = user_id
        if snippet_id:
            self.snippet_id = snippet_id

            con = self._get_db()

            sql = "SELECT * FROM snippets WHERE id = ? AND user_id = ?"
            cur = con.execute(sql, (snippet_id, self.user_id))
            snippet = cur.fetchone()
            if not snippet:
                raise ValueError("Snippet not found or access denied.")
            self.title = snippet[2]
            self.code = snippet[3]
            self.language = snippet[4]
            self.share_id = snippet[5]
        else:
            self.snippet_id = None
            self.title = title
            self.code = code
            self.language = language
            self.share_id = None

    def save(self):
        # Already saved
        if self.snippet_id:
            return

        # Validation
        if self.title.strip() == '':
            raise ValueError("Title cannot be empty.")
        if self.code.strip() == '':
            raise ValueError("Code cannot be empty.")
        if not self.language:
            raise ValueError("Language cannot be empty.")
        
        con = self._get_db()

        # Store in database
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO snippets (user_id, title, code, language, created_at) VALUES (?, ?, ?, ?, ?)"
        con.execute(sql, (self.user_id, self.title, self.code, self.language, current_time))
        con.commit()
        self.snippet_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]

    def edit(self, new_title: str, new_code: str, new_language: str):
        con = self._get_db()

        # Validation
        if new_title.strip() == '':
            raise ValueError("Title cannot be empty.")
        if new_code.strip() == '':
            raise ValueError("Code cannot be empty.")
        if not new_language:
            raise ValueError("Language cannot be empty.")

        # Update in database
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "UPDATE snippets SET title = ?, code = ?, language = ?, modified_at = ? WHERE id = ? AND user_id = ?"
        con.execute(sql, (new_title, new_code, new_language, current_time, self.snippet_id, self.user_id))
        con.commit()

    def delete(self):
        con = self._get_db()
        sql = "DELETE FROM snippets WHERE id = ? AND user_id = ?"
        con.execute(sql, (self.snippet_id, self.user_id))
        con.commit()
        self.snippet_id = None
        self.title = None
        self.code = None
        self.language = None
        self.share_id = None

    def share(self):
        if self.share_id:
            return # Already has a share_id

        con = self._get_db()
        new_share_id = str(uuid.uuid4())
        sql = "UPDATE snippets SET share_id = ? WHERE id = ? AND user_id = ?"
        con.execute(sql, (new_share_id, self.snippet_id, self.user_id))
        con.commit()
        self.share_id = new_share_id

    def unshare(self):
        if not self.share_id:
            return 
        
        con = self._get_db()
        sql = "UPDATE snippets SET share_id = NULL WHERE id = ? AND user_id = ?"
        con.execute(sql, (self.snippet_id, self.user_id))
        con.commit()
        self.share_id = None
