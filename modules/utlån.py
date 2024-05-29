from flask import Flask, render_template, request, session, redirect
import requests
from flask_cors import CORS
import os
import sqlite3
import datetime

app = Flask(__name__)
CORS(app)

con = sqlite3.Connection("./database.db", check_same_thread=False)
cur = con.cursor()

cur.execute(
    """CREATE TABLE utlån(
            id INTEGER PRIMARY KEY NOT NULL,
            bok_id INTEGER NOT NULL,
            bruker_id INTEGER NOT NULL,
            lånt TEXT NOT NULL,
            levert TEXT NOT NULL
)"""
)







@app.route("/lånte_bøker", methods=["GET"])
def lånte_bøker():
    bruker_id = request.get_json()["bruker_id"]
    cur.execute(
        "SELECT * FROM utlån WHERE bruker_id = ? AND levert = NULL", (bruker_id,)
    )


@app.route("/lån_bok/<bok_id>", methods=["POST"])
def lån_bok(bok_id):
    requests.post(
        "http://192.168.10.27/lån_bok",
        json={"bok_id": bok_id, "bruker_id": session["id"]},
    )
    return redirect("/index")





@app.route("/lånte_bøker", methods=["GET"])
def lånte_bøker():
    requests.get("http://192.168.10.27/lånte_bøker", json={"bruker_id": session["id"]})
    return render_template("lånte_bøker.html")
