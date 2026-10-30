import stat
import sqlite3
from datetime import date

db = sqlite3.connect("practice.db")

db.execute("""
CREATE TABLE IF NOT EXISTS scan_log (
  id INTEGER PRIMARY KEY,
  ticker TEXT,
  scan_date TEXT,
  conviction INTEGER,
  price REAL,
  result TEXT DEFAULT 'open'
)
""")

def log_signal(ticker, conviction, price):
    cur = db.execute(
        "INSERT INTO scan_log (ticker, scan_date, conviction, price) VALUES (?, ?, ?, ?)",
        (ticker, str(date.today()), conviction, price)
    )
    db.commit()
    print(f"Logged {ticker} as id {cur.lastrowid}")
    return cur.lastrowid

def close_signal(signal_id, result):
    db.execute("UPDATE scan_log SET result = ? WHERE id = ?", (result, signal_id))
    db.commit()

def stats():
    print("Result / Count / Avg conviction:")
    for row in db.execute(
        "SELECT result, COUNT(*), ROUND(AVG(conviction), 1) FROM scan_log GROUP BY result"
    ):
        print(row)


# pretend the scanner just found these
a = log_signal("NVDA", 9, 182.50)
b = log_signal("AMD", 6, 158.20)
close_signal(a, "win")

for row in db.execute("SELECT * FROM scan_log"):
    print(row)
stats()    