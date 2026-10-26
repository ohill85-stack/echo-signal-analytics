import sqlite3
import yfinance as yf
from datetime import date

db = sqlite3.connect("practice.db")

try:
    db.execute("ALTER TABLE real_signals ADD COLUMN price_ok INTEGER")
except sqlite3.OperationalError:
    pass

# PART A: was the logged price inside that day's real range?
tickers = [r[0] for r in db.execute("SELECT DISTINCT ticker FROM real_signals")]

for t in tickers:
    bars = yf.Ticker(t).history(start="2026-06-01", auto_adjust=False)
    days = {d: (lo, hi) for d, lo, hi in zip(bars.index.date, bars["Low"], bars["High"])}
    for rowid, sig_date, price in db.execute(
        "SELECT rowid, date, price FROM real_signals WHERE ticker = ?", (t,)
    ).fetchall():
        rng = days.get(date.fromisoformat(sig_date))
        ok = None
        if rng:
            lo, hi = rng
            ok = 1 if lo * 0.99 <= price <= hi * 1.01 else 0
            if ok == 0:
                print(f"MISMATCH {t} {sig_date}: logged {price}, Yahoo {lo:.2f}-{hi:.2f}")
        db.execute("UPDATE real_signals SET price_ok = ? WHERE rowid = ?", (ok, rowid))
db.commit()

# PART B: a clean view = first signal per ticker per day, good prices only
db.execute("DROP VIEW IF EXISTS clean_signals")
db.execute("""
    CREATE VIEW clean_signals AS
    SELECT * FROM real_signals
    WHERE price_ok = 1
      AND rowid IN (SELECT MIN(rowid) FROM real_signals GROUP BY ticker, date)
""")

print("\nClean: Conviction / Trades / Edge % / Beat SPY %:")
for row in db.execute("""
    SELECT conviction, COUNT(edge), ROUND(AVG(edge), 2),
           ROUND(100.0 * AVG(CASE WHEN edge > 0 THEN 1 ELSE 0 END), 0)
    FROM clean_signals
    WHERE edge IS NOT NULL
    GROUP BY conviction
    ORDER BY AVG(edge) DESC
"""):
    print(row)

total = db.execute("SELECT COUNT(*) FROM real_signals").fetchone()[0]
clean = db.execute("SELECT COUNT(*) FROM clean_signals").fetchone()[0]
print(f"\nAll: {total}  Clean: {clean}  Removed: {total - clean}")