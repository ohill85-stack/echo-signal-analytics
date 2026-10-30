import sqlite3, json

with open("signal_history.json") as f:
    history = json.load(f)

db = sqlite3.connect("practice.db")
db.execute("DROP TABLE IF EXISTS real_signals")
db.execute("""
CREATE TABLE real_signals (
  date TEXT, time TEXT, ticker TEXT, signal_type TEXT, price REAL,
  rsi REAL, conviction TEXT, scanner TEXT, reward_risk REAL, moat TEXT
)
""")

for s in history:
    db.execute(
        "INSERT INTO real_signals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (s["date"], s["time"], s["ticker"], s["signal_type"], s["price"],
         s["rsi"], s["conviction_level"], s["scanner"],
         s.get("reward_risk"), s.get("moat"))
    )
    db.commit()

print("Total signals:", db.execute("SELECT COUNT(*) FROM real_signals").fetchone()[0])

print("Most frequent tickers:")
for row in db.execute("SELECT ticker, COUNT(*) FROM real_signals GROUP BY ticker ORDER BY COUNT(*) DESC LIMIT 5"):
    print(row)

print("Signals by conviction:")
for row in db.execute("SELECT conviction, COUNT(*) FROM real_signals GROUP BY conviction ORDER BY COUNT(*) DESC"):
    print(row)

print("October signals by ticker:")
for row in db.execute("SELECT ticker, COUNT(*) FROM real_signals WHERE date >= '2026-10-01' GROUP BY ticker ORDER BY COUNT(*) DESC"):
        print(row)