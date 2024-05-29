from flask import Flask, request
from flask_cors import CORS
import sqlite3
import datetime

app = Flask(__name__)
CORS(app)

con = sqlite3.Connection(
    "/var/www/flask-application/database.db", check_same_thread=False
)
cur = con.cursor()


@app.route("/", methods=["GET"])
def index():
    try:
        cur.execute("SELECT * from bøker")
        bøker = cur.fetchall()
        response = []
        for bok in bøker:
            if bok[0] is not None:
                response.append(
                    {
                        "tittel": bok[0],
                        "forfatter": bok[1],
                        "isbn": bok[2],
                        "nummer": bok[3],
                        "låntaker": bok[4] if bok[4] is not None else 0,
                    }
                )
        return response, 200
    except sqlite3.Error as e:
        return {"error": str(e)}, 500


@app.route("/bok/<nummer>", methods=["GET"])
def bok(nummer):
    try:
        cur.execute("SELECT * FROM bøker WHERE nummer = ?", (nummer,))
        bok = cur.fetchone()
        if bok[0] is None:
            return {"error": "Fant ikke bok"}, 404
        response = {
            "tittel": bok[0],
            "forfatter": bok[1],
            "isbn": bok[2],
            "nummer": nummer,
            "låntaker": bok[4],
            "dato": bok[5],
        }
        return response, 200
    except sqlite3.Error as e:
        return {"error": str(e)}, 500


@app.route("/filter/<streng>", methods=["GET"])
def filter(streng):
    try:

        cur.execute(
            "SELECT * FROM bøker WHERE tittel LIKE ? OR forfatter LIKE ?",
            (f"%{streng}%", f"%{streng}%"),
        )
        bøker = cur.fetchall()
        if not bøker:
            return {"error": f"Fant ingen bøker etter søkerordet: {streng}"}, 404
        response = []
        for bok in bøker:
            response.append(
                {
                    "tittel": bok[0],
                    "forfatter": bok[1],
                    "isbn": bok[2],
                    "nummer": bok[3],
                }
            )
        return response, 200
    except sqlite3.Error as e:
        return {"error": str(e)}, 500


@app.route("/slettbok/<nummer>", methods=["DELETE"])
def slettbok(nummer):
    try:
        cur.execute("SELECT * FROM bøker WHERE nummer = ?", (nummer,))
        row = cur.fetchone()
        if row[0] is None:
            return {"error": "Boken finnes ikke i databasen"}, 404
        cur.execute(
            "UPDATE bøker SET tittel = NULL, forfatter = NULL, isbn = NULL WHERE nummer = ?",
            (nummer,),
        )
        con.commit()
        return {"melding": "Boken ble slettet fra databasen"}, 200
    except sqlite3.Error as e:
        return {"error": str(e)}, 500


@app.route("/leggtilbok", methods=["POST"])
def leggtilbok():
    try:
        tittel = request.get_json()["tittel"]
        forfatter = request.get_json()["forfatter"]
        isbn = request.get_json()["isbn"]
        nummer = request.get_json()["nummer"]
        cur.execute("SELECT * FROM bøker WHERE tittel IS NULL")
        plass = cur.fetchone()
        if plass is None:
            return {"error": "Det er ikke plass til flere bøker"}, 409
        cur.execute(
            "SELECT * FROM bøker WHERE nummer = ?",
            (nummer if nummer != 0 else plass[3],),
        )
        bok = cur.fetchone()
        if bok[0] is not None:
            return {"error": "Boken finnes fra før"}, 409
        if nummer == 0:
            cur.execute(
                "UPDATE bøker SET tittel = ?, forfatter = ?, isbn = ? WHERE nummer = ?",
                (tittel, forfatter, isbn, plass[3]),
            )
        else:
            cur.execute(
                "UPDATE bøker SET tittel = ?, forfatter = ?, isbn = ? WHERE nummer = ?",
                (tittel, forfatter, isbn, nummer),
            )
        con.commit()
        return {"melding": f"{tittel} ble registrert"}, 200
    except sqlite3.Error as e:
        return {"error": str(e)}, 500


@app.route("/registrer", methods=["POST"])
def registrer():
    try:
        navn = request.get_json()["fornavn"]
        etternavn = request.get_json()["etternavn"]
        nummer = request.get_json()["nummer"]
        cur.execute(
            "UPDATE låntakere SET fornavn = ?, etternavn = ? WHERE nummer = ?",
            (navn, etternavn, nummer),
        )
        con.commit()
        return {"melding": "Bruker lagt til"}, 200
    except sqlite3.Error as e:
        return {"error": str(e)}, 500


@app.route("/brukere", methods=["GET"])
def brukere():
    cur.execute(
        "SELECT * FROM låntakere WHERE fornavn IS NOT NULL AND etternavn IS NOT NULL"
    )
    result = cur.fetchall()
    brukere = []
    for bruker in result:
        brukere.append(
            {"fornavn": bruker[1], "etternavn": bruker[2], "nummer": bruker[0]}
        )
    return brukere, 200


@app.route("/bruker", methods=["GET"])
def bruker():
    nummer = request.get_json()["nummer"]
    cur.execute("SELECT * FROM låntakere WHERE nummer = ?", (nummer,))
    result = cur.fetchone()
    if result is not None:
        brukere = {"fornavn": result[1], "etternavn": result[2], "nummer": result[0]}
    else:
        brukere = {"melding": "Fant ikke bruker"}
    return brukere, 200


@app.route("/lån_bok", methods=["POST"])
def lån_bok():
    bok_id = request.get_json()["bok_id"]
    bruker_id = request.get_json()["bruker_id"]
    dato = datetime.datetime.now()
    cur.execute(
        "UPDATE bøker SET låntaker = ?, dato = ? WHERE nummer = ?",
        (bruker_id, dato, bok_id),
    )
    con.commit()
    return {"melding": "Bok ble lånt"}, 200


@app.route("/lever_bok", methods=["POST"])
def lever_bok():
    bok_id = request.get_json()["bok_id"]
    cur.execute(
        "UPDATE bøker SET låntaker = NULL, dato = NULL WHERE nummer = ?", (bok_id,)
    )
    con.commit()
    return {"melding": "Bok er levert"}, 200


@app.route("/aktive_lånere", methods=["GET"])
def aktive_lånere():
    cur.execute("SELECT * FROM bøker WHERE låntaker IS NOT NULL AND dato IS NOT NULL")
    bøker = cur.fetchall()
    cur.execute(
        "SELECT * FROM låntakere WHERE fornavn IS NOT NULL AND etternavn IS NOT NULL"
    )
    brukere = cur.fetchall()
    bokliste = []
    brukerliste = []
    for bok in bøker:
        bokliste.append(
            {
                "tittel": bok[0],
                "forfatter": bok[1],
                "isbn": bok[2],
                "nummer": bok[3],
                "låntaker": bok[4],
                "dato": bok[5],
            }
        )
    for bruker in brukere:
        brukerliste.append(
            {"fornavn": bruker[1], "etternavn": bruker[2], "nummer": bruker[0]}
        )
    return [bokliste, brukerliste], 200


if __name__ == "__main__":
    app.run(debug=True, port=5010)
