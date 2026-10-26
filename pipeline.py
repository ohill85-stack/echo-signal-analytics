import sqlite3, json
import yfinance as yf
from datetime import date

DB = "practice.db"
START = "2026-06-01"


def load_signals(db):
    with open("signal_history.json") as f:
        history = json.load(f)
    db.execute("DROP VIEW IF EXISTS clean_signals")
    db.execute("DROP TABLE IF EXISTS real_signals")
    db.execute("""
        CREATE TABLE real_signals (
          date TEXT, time TEXT, ticker TEXT, price REAL, conviction TEXT, scanner TEXT,
          price_ok INTEGER, fwd_return REAL, outcome TEXT, spy_return REAL, edge REAL
        )
    """)
    for s in history:
        db.execute(
            "INSERT INTO real_signals (date, time, ticker, price, conviction, scanner) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (s["date"], s["time"], s["ticker"], s["price"], s["conviction_level"], s["scanner"]),
        )
    print(f"Loaded {len(history)} signals")


def get_bars(ticker, cache):
    if ticker not in cache:
        bars = yf.Ticker(ticker).history(start=START, auto_adjust=False)
        bars = bars.dropna(subset=["Close"])
        cache[ticker] = bars[bars.index.date < date.today()]
    return cache[ticker]


def score_signals(db):
    cache = {}
    spy = get_bars("SPY", cache)
    rows = db.execute("SELECT rowid, ticker, date, price FROM real_signals").fetchall()
    for rowid, ticker, sig_date, price in rows:
        d = date.fromisoformat(sig_date)
        bars = get_bars(ticker, cache)

        price_ok = None
        that_day = bars[bars.index.date == d]
        if not that_day.empty:
            lo, hi = float(that_day["Low"].iloc[0]), float(that_day["High"].iloc[0])
            price_ok = 1 if lo * 0.99 <= price <= hi * 1.01 else 0

        fwd = outcome = spy_ret = edge = None
        after = bars[bars.index.date > d]
        spy_before = spy[spy.index.date <= d]
        spy_after = spy[spy.index.date > d]
        if len(after) >= 5 and len(spy_after) >= 5 and not spy_before.empty:
            fwd = round((float(after["Close"].iloc[4]) - price) / price * 100, 2)
            outcome = "win" if fwd > 0 else "loss"
            s0 = float(spy_before["Close"].iloc[-1])
            s5 = float(spy_after["Close"].iloc[4])
            spy_ret = round((s5 - s0) / s0 * 100, 2)
            edge = round(fwd - spy_ret, 2)

        db.execute(
            "UPDATE real_signals SET price_ok=?, fwd_return=?, outcome=?, spy_return=?, edge=? "
            "WHERE rowid=?",
            (price_ok, fwd, outcome, spy_ret, edge, rowid),
        )
    print(f"Scored {len(rows)} signals with {len(cache)} price downloads")


def build_clean_view(db):
    db.execute("""
        CREATE VIEW clean_signals AS
        SELECT * FROM real_signals
        WHERE price_ok = 1
          AND rowid IN (SELECT MIN(rowid) FROM real_signals GROUP BY ticker, date)
    """)


def report(db):
    total = db.execute("SELECT COUNT(*) FROM real_signals").fetchone()[0]
    clean = db.execute("SELECT COUNT(*) FROM clean_signals").fetchone()[0]
    scored = db.execute("SELECT COUNT(*) FROM clean_signals WHERE edge IS NOT NULL").fetchone()[0]
    print(f"\nAll: {total}  Clean: {clean}  Scored: {scored}")

    for group in ["conviction", "scanner"]:
        print(f"\n{group.title()} / Trades / Avg % / Edge % / Beat SPY %")
        for row in db.execute(f"""
            SELECT {group}, COUNT(edge), ROUND(AVG(fwd_return), 2), ROUND(AVG(edge), 2),
                   ROUND(100.0 * AVG(CASE WHEN edge > 0 THEN 1 ELSE 0 END), 0)
            FROM clean_signals
            WHERE edge IS NOT NULL
            GROUP BY {group}
            ORDER BY AVG(edge) DESC
        """):
            print(row)


def top_and_worst(db):
    print("\nTop 3 vs SPY:")
    for row in db.execute(
        "SELECT ticker, date, conviction, edge FROM clean_signals "
        "WHERE edge IS NOT NULL ORDER BY edge DESC LIMIT 3"
    ):
        print(row)

    print("\nWorst 3 vs SPY:")
    for row in db.execute(
        "SELECT ticker, date, conviction, edge FROM clean_signals "
        "WHERE edge IS NOT NULL ORDER BY edge ASC LIMIT 3"
    ):
        print(row)


def main():
    db = sqlite3.connect(DB)
    load_signals(db)
    score_signals(db)
    build_clean_view(db)
    db.commit()
    report(db)
    top_and_worst(db)
    db.close()


if __name__ == "__main__":
    main()