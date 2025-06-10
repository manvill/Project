import time
import sqlite3
import json
import os

class TokenCache:
    def __init__(self, db_path="tokens.db"):
        self.db_path = db_path
        self._init_db()
        self.last_refresh_time = 0
        self.max_duration = 7 * 24 * 60 * 60  # 7 days

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True) if os.path.dirname(self.db_path) else None
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS tokens (
                            tokenAddress TEXT PRIMARY KEY,
                            data TEXT,
                            fetched_at REAL)''')

    def update_tokens(self, new_tokens):
        with sqlite3.connect(self.db_path) as conn:
            for token in new_tokens:
                # Check if token already exists → keep old fetched_at
                row = conn.execute("SELECT fetched_at FROM tokens WHERE tokenAddress = ?", (token["tokenAddress"],)).fetchone()
                fetched_at = row[0] if row else token["fetched_at"]
                conn.execute("REPLACE INTO tokens (tokenAddress, data, fetched_at) VALUES (?, ?, ?)",
                             (token["tokenAddress"], json.dumps(token), fetched_at))

    def get_tokens(self):
        cutoff = time.time() - self.max_duration
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT data FROM tokens WHERE fetched_at > ? ORDER BY fetched_at DESC", (cutoff,)).fetchall()
            return [json.loads(row[0]) for row in rows]