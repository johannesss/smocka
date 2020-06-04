import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from os.path import dirname

root_dir_path = dirname(os.path.dirname(os.path.abspath(__file__)))
db_file_path = root_dir_path + '/.db/db.sqlite'
schema_file_path = root_dir_path + '/app/database/schema.sql'


def generate_uuid():
    return str(uuid.uuid4())


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_connection():
    conn = sqlite3.connect(db_file_path)
    conn.row_factory = _dict_factory

    return conn


def get_response_repository():
    conn = get_connection()
    return ResponseSqliteRepository(conn)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        with open(schema_file_path) as f:
            cursor.executescript(f.read())
    except IOError as e:
        print(e)


class ResponseSqliteRepository():
    def __init__(self, connection):
        self.conn = connection

    def __del__(self):
        self.conn.close()

    def delete_by_id(self, id):
        cursor = self.conn.cursor()

        cursor.execute('DELETE FROM response WHERE id = ?', (id, ))

        self.conn.commit()

        return True

    def find_by_uuid(self, uuid):
        cursor = self.conn.cursor()

        cursor.execute('SELECT * FROM response WHERE uuid = ?', (uuid, ))

        return cursor.fetchone()

    def find_by_id(self, id):
        cursor = self.conn.cursor()

        cursor.execute('SELECT * FROM response WHERE id = ?', (id, ))

        return cursor.fetchone()

    def create(self, status_code, content_type, ttl, body):
        created = datetime.now()

        if ttl is not None:
            ttl = created + timedelta(minutes=ttl)

        values = (generate_uuid(), status_code,
                  content_type,  body, created, ttl)

        cursor = self.conn.cursor()

        query = 'INSERT INTO response (uuid, status_code, content_type, body, created, expires) VALUES (?, ?, ?, ?, ?, ?)'  # noqa
        cursor.execute(query, values)

        self.conn.commit()

        return self.find_by_id(str(cursor.lastrowid))
