import sqlite3
import yfinance as yf
from datetime import date

db = sqlite3.connect("practice.db")

for col in ["spy_return REAL", "edge REAL"]:
    try:
        db.execute(f"ALTER TABLE real_signals ADD COLUMN {col}")
    except sqlite3.OperationalError:
        pass

db.execute("UPDATE real_signals SET spy_return = NULL, edge = NULL")

# download SPY ONCE for the whole period
spy = yf.Ticker("SPY").history(start="2026-06-01")
spy = spy.dropna(subset=["Close"])
spy = spy[spy.index.date < date.today()]

rows = db.execute(
    "SELECT rowid, date, fwd_return FROM real_signals WHERE fwd_return IS NOT NULL"
).fetchall()

for rowid, sig_date, fwd in rows:
    d = date.fromisoformat(sig_date)
    before = spy[spy.index.date <= d]
    after = spy[spy.index.date > d]
    if before.empty or len(after) < 5:
        continue
    spy_start = float(before["Close"].iloc[-1])
    spy_end = float(after["Close"].iloc[4])
    spy_ret = round((spy_end - spy_start) / spy_start * 100, 2)
    edge = round(fwd - spy_ret, 2)
    db.execute("UPDATE real_signals SET spy_return = ?, edge = ? WHERE rowid = ?",
               (spy_ret, edge, rowid))

db.commit()

print("Conviction / Trades / Avg % / SPY % / Edge % / Beat SPY %:")
for row in db.execute("""
    SELECT conviction, COUNT(edge),
           ROUND(AVG(fwd_return), 2), ROUND(AVG(spy_return), 2), ROUND(AVG(edge), 2),
           ROUND(100.0 * AVG(CASE WHEN edge > 0 THEN 1 ELSE 0 END), 0)
    FROM real_signals
    WHERE edge IS NOT NULL AND date >= '2026-09-01'
    GROUP BY conviction
    ORDER BY AVG(edge) DESC
"""):
    print(row)

print("\nTop 3 signals vs SPY:")
for row in db.execute(
    "SELECT ticker, date, edge FROM real_signals WHERE edge IS NOT NULL ORDER BY edge DESC LIMIT 3"
):
    print(row)

print("\nWorst 3 signals vs SPY:")
for row in db.execute(
    "SELECT ticker, date, edge FROM real_signals WHERE edge IS NOT NULL ORDER BY edge ASC LIMIT 3"
):
    print(row)