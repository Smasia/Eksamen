from flask import Flask, render_template, request
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/bok/", methods=["GET"])
def bok():
    nummer = request.form.get("nummer")
    response = requests.get("http://192.168.10.27/bok/" + str(nummer))
    return render_template("bok.html", bok=response)


if __name__ == "__main__":
    app.run(debug=True)
