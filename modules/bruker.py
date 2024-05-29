from flask import Flask, render_template, request, session, redirect
import requests
from flask_cors import CORS
import os
import sqlite3

app = Flask(__name__)
CORS(app)

con = sqlite3.Connection("./database.db", check_same_thread=False)
cur = con.cursor()

app.secret_key = b"uirhfuierjhferhf84738420967ryh73yr73y408hf0876gd0"
session["navn"] = ""
session["id"] = 0


def logget_inn(func):
    def wrapper(*args, **kwargs):
        if "navn" in session:
            return func()
        return redirect("/logg_inn")

    return wrapper


cur.execute(
    """CREATE TABLE brukere(
            id INTEGER PRIMARY KEY NOT NULL,
            navn TEXT NOT NULL,
            passord TEXT NOT NULL,
            låner_bok integer
)"""
)


@app.route("/registrer", methods=["POST"])
def registrer():
    try:
        navn = request.get_json()["navn"]
        passord = request.get_json()["passord"]
        cur.execute("INSERT INTO brukere(navn, passord) VALUES(?, ?)", (navn, passord))
        con.commit()
        return {"melding": "Bruker lagt til"}, 200
    except sqlite3.Error as e:
        return {"error": str(e)}, 500


@app.route("/logg_inn", methods=["POST"])
def logg_inn():
    try:
        navn = request.get_json()["navn"]
        passord = request.get_json()["passord"]
        cur.execute(
            "SELECT * FROM brukere WHERE navn = ? AND passord = ?", (navn, passord)
        )
        bruker = cur.fetchone()
        if bruker is None:
            return {"melding": "fant ikke bruker"}, 404
        return {"navn": bruker[1], "id": bruker[0]}, 200
    except sqlite3.Error as e:
        return {"error": str(e)}, 500


@app.route("/registrer", methods=["GET", "POST"])
def registrer():
    if request.method == "GET":
        return render_template("registrer.html")

    if request.method == "POST":
        navn = request.form.get("navn")
        passord = request.form.get("passord")
        requests.post(
            "http://192.168.10.27/registrer", json={"navn": navn, "passord": passord}
        )
        return redirect("/logg_inn")


@app.route("/logg_inn", methods=["GET", "POST"])
def logg_inn():
    if request.method == "GET":
        return render_template("logg_inn.html")

    if request.method == "POST":
        navn = request.form.get("navn")
        passord = request.form.get("passord")
        response = requests.post(
            "http://192.168.10.27/logg_inn", json={"navn": navn, "passord": passord}
        )
        if response.status_code == 404:
            return render_template("logg_inn.html", melding=response.json()["melding"])
        session["id"] = response.json()["id"]
        session["navn"] = response.json()["navn"]
        return redirect("/index")
