from flask import render_template, redirect, url_for, abort
from snippet import Snippet
from levenshtein import fuzzy_search

class SnippetController:
    _LANGS = {
        "python": 'Python',
        "javascript": 'JavaScript',
        "java": 'Java',
        "cpp": 'C++',
        "csharp": 'C#',
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
        if title.strip() == '':
            return render_template('new.html', error='Title cannot be empty.')
        if language.strip() == '':
            return render_template('new.html', error='Language cannot be empty.')
        if code.strip() == '':
            return render_template('new.html', error='Code cannot be empty.')
        
        snippet = Snippet(self._get_db, user_id, title, code, language)
        snippet.save()

        return redirect(url_for('snippet', id=snippet.snippet_id))
    
    def search_snippets(self, user_id, query, sort, include_code, fuzzy):
        con = self._get_db()

        if fuzzy:
            sql = "SELECT * FROM snippets WHERE user_id = ?"
            cur = con.execute(sql, (user_id,))
            snippets = cur.fetchall()
            
            filtered_snippets = []
            
            for snippet in snippets:
                if fuzzy_search(snippet[2].lower(), query) or (include_code and fuzzy_search(snippet[3].lower(), query)):
                    filtered_snippets.append(snippet)

            snippets = filtered_snippets
        else:
            if include_code:
                sql = "SELECT * FROM snippets WHERE user_id = ? AND (title LIKE ? OR code LIKE ?)"
                cur = con.execute(sql, (user_id, f'%{query}%', f'%{query}%'))
            else:
                sql = "SELECT * FROM snippets WHERE user_id = ? AND title LIKE ?"
                cur = con.execute(sql, (user_id, f'%{query}%'))

            snippets = cur.fetchall()

        snippets_arr = []
        for snippet in snippets:
            snippets_arr.append(self._get_snippet_dict(snippet))
        
        match sort:
            case 'recent':
                snippets_arr.sort(key=lambda x: x['modified_at'] or x['created_at'], reverse=True)
            case 'title':
                snippets_arr.sort(key=lambda x: x['title'].lower())
            case 'language':
                snippets_arr.sort(key=lambda x: x['language'].lower())

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