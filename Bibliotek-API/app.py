from flask import Flask, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

con = sqlite3.Connection("./database.db", check_same_thread=False)
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
        cur.execute("SELECT * FROM bøker WHERE nummer = ?", (nummer,))
        bok = cur.fetchone()
        if bok[0] is not None:
            return {"error": "Boken finnes fra før"}, 409
        cur.execute(
            "UPDATE bøker SET tittel = ?, forfatter = ?, isbn = ? WHERE nummer = ?",
            (tittel, forfatter, isbn, nummer),
        )
        con.commit()
        return {"melding": f"{tittel} ble registrert"}, 200
    except sqlite3.Error as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(debug=True, port=5010)
