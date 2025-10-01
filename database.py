def create_table(name: str, columns: dict, get_db):
    con = get_db()
    cols = ', '.join([f"{col} {' '.join(props)}" for col, props in columns.items()])
    sql = f"CREATE TABLE IF NOT EXISTS {name} ({cols})"
    con.execute(sql)

def init_tables(get_db):
    user_columns = {
        'id': ['INTEGER', 'PRIMARY KEY', 'AUTOINCREMENT'],
        'username': ['TEXT', 'UNIQUE', 'NOT NULL'],
        'password': ['TEXT', 'NOT NULL']
    }

    snippet_columns = {
        'id': ['INTEGER', 'PRIMARY KEY', 'AUTOINCREMENT'],
        'user_id': ['INTEGER', 'NOT NULL'],
        'title': ['TEXT', 'NOT NULL'],
        'code': ['TEXT', 'NOT NULL'],
        'language': ['TEXT'],
        'created_at': ['TIMESTAMP', 'DEFAULT CURRENT_TIMESTAMP'],
        'FOREIGN KEY(user_id)': ['REFERENCES users(id)']
    }

    create_table('users', user_columns, get_db)
    create_table('snippets', snippet_columns, get_db)