from flask import Flask, render_template, request
import requests
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def index():
    response = requests.get("http://192.168.10.27/")
    return render_template("index.html", bøker=response.json())


@app.route("/bok/", methods=["GET"])
def bok():
    nummer = request.args.get("nummer")
    print(nummer)
    response = requests.get("http://192.168.10.27/bok/" + str(nummer))
    print(response.json())
    return render_template("bok.html", bok=response.json())


@app.route("/barcode/<nummer>", methods=["GET"])
def barcode(nummer):
    path = "E:\\Eksamen\\Bibliotek-frontend\\static\\barcode\\"
    barcode = os.path.join(path, f"{nummer}.png")
    print(barcode)
    return barcode


if __name__ == "__main__":
    app.run(debug=True)
