import sqlite3

db = sqlite3.connect("practice.db")

db.execute("""
CREATE TABLE IF NOT EXISTS signals (
  id INTEGER PRIMARY KEY,
  ticker TEXT,
  scan_date TEXT,
  conviction INTEGER,
  entry_price REAL,
  result TEXT
)
""")

db.execute("""
INSERT INTO signals (ticker, scan_date, conviction, entry_price, result)
VALUES ('NVDA', '2026-10-19', 6, 182.50, 'win')
""")

db.commit()

for row in db.execute("SELECT ticker, conviction FROM signals WHERE ticker = 'NVDA' AND result = 'win'"):
    print(row)