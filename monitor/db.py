import sqlite3
from pathlib import Path

SCHEMA = '''
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    cpu REAL,
    mem REAL,
    net_sent INTEGER,
    net_recv INTEGER,
    processes INTEGER
);
'''

class DB:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.execute('PRAGMA journal_mode=WAL;')

    def init_tables(self):
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def insert_sample(self, timestamp, cpu, mem, net_sent, net_recv, processes):
        cur = self.conn.cursor()
        cur.execute(
            'INSERT INTO metrics (timestamp, cpu, mem, net_sent, net_recv, processes) VALUES (?, ?, ?, ?, ?, ?)',
            (timestamp, cpu, mem, net_sent, net_recv, processes)
        )
        self.conn.commit()

    def fetch_recent(self, limit=100):
        cur = self.conn.cursor()
        cur.execute('SELECT timestamp, cpu, mem, net_sent, net_recv, processes FROM metrics ORDER BY timestamp DESC LIMIT ?', (limit,))
        return cur.fetchall()
