import sqlite3

con = sqlite3.connect(
    "database.db",
    check_same_thread=False,
)
cur = con.cursor()


cur.execute(
    """CREATE TABLE IF NOT EXISTS bøker(
            tittel TEXT,
            forfatter TEXT,
            isbn INTEGER,
            nummer INTEGER UNIQUE NOT NULL,
            låntaker INTEGER,
            dato TEXT
)"""
)
con.commit()

cur.execute(
    """CREATE TABLE låntakere(
            nummer INTEGER PRIMARY KEY NOT NULL,
            fornavn TEXT,
            etternavn TEXT
)"""
)
con.commit()

cur.executemany(
    "INSERT INTO bøker(nummer) VALUES(?)", [(nummer,) for nummer in range(1, 52)]
)
con.commit()

cur.executemany(
    "INSERT INTO låntakere(nummer) VALUES(?)",
    [(nummer,) for nummer in range(1000, 1021)],
)
con.commit()

bokliste = []
with open("./bøker.csv", "r", encoding="utf-8") as file:
    bøker = [bok for bok in file.read().split("\n")]
    for bok in bøker:
        d_bok = bok.split(",")
        bokliste.append(
            {
                "tittel": d_bok[0],
                "forfatter": d_bok[1],
                "isbn": d_bok[2],
                "nummer": d_bok[3],
            }
        )

cur.executemany(
    "UPDATE bøker SET tittel = ?, forfatter = ?, isbn = ? WHERE nummer = ?",
    [(bok["tittel"], bok["forfatter"], bok["isbn"], bok["nummer"]) for bok in bokliste],
)
con.commit()
