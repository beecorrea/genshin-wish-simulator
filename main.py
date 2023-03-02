import wish
import sqlite3

db = sqlite3.connect("wishes.db")
c = db.cursor()

w = wish.Wish(avg_rounds_per_game=100)
outcomes = []
print("====Starting====")
for i in range(w.avg_rounds_per_game):
    ot = w.wish()
    outcomes.append(ot)

c.executemany("INSERT INTO wish (outcome, hit_type) VALUES (?, ?)", outcomes)
db.commit()
db.close()
