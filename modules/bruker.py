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
