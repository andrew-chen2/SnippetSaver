from flask import render_template, redirect, url_for, abort, flash
from snippet import Snippet
from levenshtein import fuzzy_search
from snippets.detectors.detect_cpp import detect_cpp_snippets
from snippets.detectors.detect_html import detect_html_snippets
from snippets.detectors.detect_javascript import detect_javascript_snippets
from snippets.detectors.detect_python import detect_python_snippets

class SnippetController:
    _LANGS = {
        "python": 'Python',
        "javascript": 'JavaScript',
        "cpp": 'C++',
        "html": 'HTML',
        "other": 'Other',
    }

    def __init__(self, get_db):
        self._get_db = get_db

    def _get_snippet_dict(self, snippet):
        return {
            'id': snippet[0],
            'user_id': snippet[1],
            'title': snippet[2],
            'code': snippet[3],
            'language': self._LANGS[snippet[4]],
            'share_id': snippet[5],
            'created_at': snippet[6],
            'modified_at': snippet[7],
        }
    
    def validate_snippet(self, title, code, language, url):
        if len(title) > 128 or len(code) > 10000:
            flash('Title or code exceeds maximum length.', 'error')
            return redirect(url)
        if title.strip() == '':
            flash('Title cannot be empty.', 'error')
            return redirect(url)
        if language.strip() == '':
            flash('Language cannot be empty.', 'error')
            return redirect(url)
        if code.strip() == '':
            flash('Code cannot be empty.', 'error')
            return redirect(url)
        if language not in self._LANGS:
            flash('Invalid language selected.', 'error')
            return redirect(url)  

    def get_snippet_from_id(self, id, user_id):
        try:
            snippet = Snippet(self._get_db, user_id, snippet_id=id)
            return snippet
        except ValueError:
            abort(404)
    
    def get_snippet(self, id, user_id):
        con = self._get_db()
        sql = "SELECT * FROM snippets WHERE id = ? AND user_id = ?"
        cur = con.execute(sql, (id, user_id))
        snippet = cur.fetchone()
        if snippet:
            snippet_dict = self._get_snippet_dict(snippet)
            return snippet_dict
        return None
    
    def get_user_snippets(self, user_id):
        con = self._get_db()
        sql = "SELECT * FROM snippets WHERE user_id = ? ORDER BY modified_at DESC"
        cur = con.execute(sql, (user_id,))
        snippets = cur.fetchall()
        snippets_arr = []
        for snippet in snippets:
            snippets_arr.append(self._get_snippet_dict(snippet))
        return snippets_arr

    def create_snippet(self, user_id, title, code, language):
        validated = self.validate_snippet(title, code, language, url_for('snippet', id='new'))
        if validated:
            return validated
        
        snippet = Snippet(self._get_db, user_id, title, code, language)
        snippet.save()

        return redirect(url_for('snippet', id=snippet.snippet_id))
    
    def search_snippets(self, user_id, query, sort, include_code, fuzzy, language, shared):
        con = self._get_db()

        # Base SQL query
        sql = "SELECT * FROM snippets WHERE user_id = ?"
        params = [user_id]

        # Dynamically build SQL query
        if language:
            sql += " AND language = ?"
            params.append(language)

        if shared == 'yes':
            sql += " AND share_id IS NOT NULL"
        elif shared == 'no':
            sql += " AND share_id IS NULL"

        # Get snippets
        if fuzzy:
            cur = con.execute(sql, tuple(params))
            snippets = cur.fetchall()
            
            filtered_snippets = []
            
            for snippet in snippets:
                if fuzzy_search(snippet[2].lower(), query) or (include_code and fuzzy_search(snippet[3].lower(), query)):
                    filtered_snippets.append(snippet)

            snippets = filtered_snippets
        else:
            params.append(f'%{query}%')
            if include_code:
                sql += " AND (title LIKE ? OR code LIKE ?)"
                params.append(f'%{query}%')
            else:
                sql += " AND title LIKE ?"

            cur = con.execute(sql, tuple(params))
            snippets = cur.fetchall()

        # Get snippets as a list of dicts
        snippets_arr = []
        for snippet in snippets:
            snippets_arr.append(self._get_snippet_dict(snippet))
        
        # Sort snippets
        """ match sort:
            case 'recent':
                snippets_arr.sort(key=lambda x: x['modified_at'] or x['created_at'], reverse=True)
            case 'title':
                snippets_arr.sort(key=lambda x: x['title'].lower()) """
        if sort == 'recent':
            snippets_arr.sort(key=lambda x: x['modified_at'] or x['created_at'], reverse=True)
        elif sort == 'title':
            snippets_arr.sort(key=lambda x: x['title'].lower())

        return render_template('library.html', snippets = snippets_arr)

    def get_shared_snippet(self, share_id, user_id):
        con = self._get_db()
        sql = "SELECT * FROM snippets WHERE share_id = ?"
        cur = con.execute(sql, (share_id,))
        snippet = cur.fetchone()
        if snippet:
            snippet_dict = self._get_snippet_dict(snippet)
            # Get username of owner
            sql = "SELECT username FROM users WHERE id = ?"
            cur = con.execute(sql, (snippet[1],))
            owner = cur.fetchone()
            if owner:
                snippet_dict['owner_username'] = owner[0]
            else:
                snippet_dict['owner_username'] = 'Deleted User'
            own_snippet = snippet_dict['user_id'] == user_id
            return render_template('shared.html', snippet=snippet_dict, own_snippet=own_snippet)
        abort(404)

    def add_shared_snippet(self, share_id, user_id):
        con = self._get_db()
        sql = "SELECT * FROM snippets WHERE share_id = ?"
        cur = con.execute(sql, (share_id,))
        snippet = cur.fetchone()
        if snippet:
            if snippet[1] == user_id:
                return redirect(url_for('snippet', id=snippet[0]))
            snippet = Snippet(self._get_db, user_id, snippet[2], snippet[3], snippet[4])
            snippet.save()
            return redirect(url_for('snippet', id=snippet.snippet_id))
        abort(404)

    def get_detected_snippets(self, code, lang):
        if not code.strip():
            return []
        """ match lang:
            case 'python':
                return detect_python_snippets(code)
            case 'javascript':
                return detect_javascript_snippets(code)
            case 'cpp':
                return detect_cpp_snippets(code)
            case 'html':
                return detect_html_snippets(code)
            case _:
                return [] """
        if lang == 'python':
            return detect_python_snippets(code)
        elif lang == 'javascript':
            return detect_javascript_snippets(code)
        elif lang == 'cpp':
            return detect_cpp_snippets(code)
        elif lang == 'html':
            return detect_html_snippets(code)
        else:
            return []
