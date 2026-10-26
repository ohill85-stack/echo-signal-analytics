import sqlite3
db = sqlite3.connect("practice.db")

db.execute("DELETE FROM signals WHERE id = 3")
db.execute("UPDATE signals SET result = 'loss' WHERE id = 1")
db.commit()

for row in db.execute("SELECT * FROM signals"):
    print(row)

print(db.execute("SELECT COUNT(*) FROM signals WHERE result = 'win' or result = 'loss'").fetchone())