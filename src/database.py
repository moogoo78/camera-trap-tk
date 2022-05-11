import sqlite3
import logging

SQL_INIT_SOURCE = '''
CREATE TABLE IF NOT EXISTS source (
  source_id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_type TEXT,
  path TEXT,
  name TEXT,
  count INTEGER,
  created INTEGER,
  status TEXT,
  description TEXT,
  history TEXT,
  trip_start TEXT,
  trip_end TEXT,
  test_foto_time TEXT,
  deployment_journal_id INTEGER
);'''

SQL_INIT_IMAGE = '''
CREATE TABLE IF NOT EXISTS image (
  image_id INTEGER PRIMARY KEY AUTOINCREMENT,
  path TEXT,
  name TEXT,
  timestamp INTEGER,
  timestamp_via TEXT,
  status TEXT,
  hash TEXT,
  annotation TEXT,
  changed INTEGER,
  exif TEXT,
  source_id INTEGER,
  server_image_id TEXT,
  upload_status TEXT,
  sys_note TEXT,
  object_id TEXT,
  FOREIGN KEY (source_id) REFERENCES source(source_id)
);'''

class Database(object):
    conn = None
    cursor = None

    # PRAGMA table_info('source')
    # PRAGMA table_info('image')

    def __init__(self, db_file):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        self.conn = conn
        self.cursor = cursor

    def init(self):
        self.cursor.execute(SQL_INIT_SOURCE)
        self.cursor.execute(SQL_INIT_IMAGE)

    def exec_sql(self, sql, commit=False):
        logging.debug(sql)
        self.cursor.execute(sql)

        if commit:
            self.conn.commit()
        return self.cursor.lastrowid

    def fetch_sql_all(self, sql):
        rows = []
        for r in self.cursor.execute(sql):
            rows.append(r)
        return rows

    def fetch_sql(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()
