from sqlite3 import connect

con = connect('snippetsaver.db')

def create_table(name: str, columns: dict):
    cols = ', '.join([f"{col} {' '.join(props)}" for col, props in columns.items()])
    sql = f"CREATE TABLE IF NOT EXISTS {name} ({cols})"
    con.execute(sql)
    con.commit()

def init_tables():
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
        'share_id': ['TEXT', 'UNIQUE'],
        'created_at': ['TIMESTAMP', 'DEFAULT CURRENT_TIMESTAMP'],
        'modified_at': ['TIMESTAMP', 'DEFAULT CURRENT_TIMESTAMP'],
        'FOREIGN KEY(user_id)': ['REFERENCES users(id)']
    }

    create_table('users', user_columns)
    create_table('snippets', snippet_columns)

def delete_rows(tables: list):
    if not tables:
        return
    for table in tables:
        sql = "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?"
        if con.execute(sql, (table,)).fetchone():
            con.execute(f"DELETE FROM {table}")
    con.commit()