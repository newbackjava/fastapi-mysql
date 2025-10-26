import os
import pymysql  # PyMySQL
from typing import Optional

class MySQLSync:
    def __init__(self):
        self.conn: Optional[pymysql.connections.Connection] = None

    def connect(self):
        if self.conn:
            return
        host = os.getenv("MYSQL_HOST", "127.0.0.1")
        port = int(os.getenv("MYSQL_PORT", "3307"))  # default to 3307
        user = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD", "1234")
        db = os.getenv("MYSQL_DATABASE", "demo_db")

        self.conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db,
            autocommit=True,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.Cursor,
        )

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute(self, sql: str, params: tuple = ()):
        assert self.conn is not None, "DB not connected. Call connect() first."
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur

mysql_sync = MySQLSync()
