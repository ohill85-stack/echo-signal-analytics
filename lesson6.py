import sqlite3
import yfinance as yf
from datetime import date, timedelta

db = sqlite3.connect("practice.db")

# add new columns (skips if they already exist)
for col in ["fwd_return REAL", "outcome TEXT"]:
    try:
        db.execute(f"ALTER TABLE real_signals ADD COLUMN {col}")
    except sqlite3.OperationalError:
        pass
db.execute("UPDATE real_signals SET fwd_return = NULL, outcome = NULL")
rows = db.execute("SELECT rowid, ticker, date, price FROM real_signals").fetchall()

for rowid, ticker, sig_date, price in rows:
    start = date.fromisoformat(sig_date) + timedelta(days=1)
    bars = yf.Ticker(ticker).history(start=start, end=start + timedelta(days=14))
    bars = bars.dropna(subset=["Close"])
    bars = bars[bars.index.date < date.today()]
    if len(bars) < 5:
        print(f"{ticker} {sig_date}: not enough days yet")
        continue
    close_5 = float(bars["Close"].iloc[4])
    fwd = round((close_5 - price) / price * 100, 2)
    outcome = "win" if fwd > 0 else "loss"
    db.execute  ("UPDATE real_signals SET fwd_return = ?, outcome = ? WHERE rowid = ?",
               (fwd, outcome, rowid))
    print(f"{ticker} {sig_date}: {fwd}% {outcome}")

db.commit()

print("\nScanner / Trades / Avg % / Win rate %:")
for row in db.execute("""
    SELECT scanner, COUNT(fwd_return), ROUND(AVG(fwd_return), 2),
           ROUND(100.0 * AVG(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END), 0)
    FROM real_signals
    WHERE fwd_return IS NOT NULL
    GROUP BY scanner
    ORDER BY AVG(fwd_return) DESC
"""):
    print(row)