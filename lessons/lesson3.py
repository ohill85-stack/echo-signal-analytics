import sqlite3
db = sqlite3.connect("practice.db")

# fresh practice table every run
db.execute("DROP TABLE IF EXISTS trades")
db.execute("CREATE TABLE trades (ticker TEXT, conviction INTEGER, result TEXT, pnl REAL)")

sample = [
    ("NVDA", 9, "win", 320), ("NVDA", 8, "win", 150), ("NVDA", 6, "loss", -90),
    ("AMD", 7, "win", 110), ("AMD", 5, "loss", -140), ("AMD", 8, "loss", -60),
    ("TSLA", 9, "win", 410), ("TSLA", 6, "loss", -200), ("TSLA", 7, "win", 90),
]
db.executemany("INSERT INTO trades VALUES (?, ?, ?, ?)", sample)
db.commit()

print("Trades by result:")
for row in db.execute("SELECT result, COUNT(*) FROM trades GROUP BY result"):
    print(row)

print("Avg conviction by result:")
for row in db.execute("SELECT result, ROUND(AVG(conviction), 1) FROM trades GROUP BY result"):
    print(row)

print("Total P&L by ticker:")
for row in db.execute("SELECT ticker, SUM(pnl) FROM trades GROUP BY ticker"):
    print(row)

print("Average P&L by ticker (best first):")
for row in db.execute("SELECT ticker,ROUND(AVG(pnl), 2) FROM trades GROUP BY ticker ORDER BY AVG(pnl) DESC"):
    print(row)

