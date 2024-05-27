from flask import Flask, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

con = sqlite3.Connection("database.db", check_same_thread=False)  # connection
cur = con.cursor()  # cursor


@app.route("/", methods=["GET"])
def index():
    try:
        cur.execute("SELECT * from bøker")
        bøker = cur.fetchall()
        response = []
        for bok in bøker:
            response.append(
                {
                    "tittel": bok[0],
                    "forfatter": bok[1],
                    "isbn": int(bok[2]),
                    "nummer": int(bok[3]),
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
    except TypeError:
        return {"error": "Fant ikke bok"}, 404


if __name__ == "__main__":
    app.run(debug=True)
