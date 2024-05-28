from flask import Flask, render_template, request, redirect
import requests
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def index():
    response = requests.get("http://192.168.10.27/")
    return render_template("index.html", bøker=response.json())


@app.route("/bok/<int:nummer>", methods=["GET"])
def bok(nummer):
    if nummer == 0:
        nummer = request.args.get("nummer")
    if int(nummer) < 1 or int(nummer) > 51:
        return {"nummer": "Bok nummer utenfor rekkevidden"}, 404
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


@app.route("/filter", methods=["GET"])
def filter():
    streng = request.args.get("streng")
    response = requests.get("http://192.168.10.27:/filter/" + streng)
    return render_template("index.html", bøker=response.json(), streng=streng)


@app.route("/slettbok/<nummer>", methods=["POST"])
def slettbok(nummer):
    requests.delete("http://192.168.10.27:/slettbok/" + nummer)
    return redirect("/")


@app.route("/leggtilbok", methods=["GET", "POST"])
def leggtilbok():
    if request.method == "GET":
        return render_template("leggtilbok.html")

    if request.method == "POST":
        tittel = request.form.get("tittel")
        forfatter = request.form.get("forfatter")
        isbn = request.form.get("isbn")
        nummer = request.form.get("nummer")
        requests.post(
            "http://192.168.10.27:/leggtilbok",
            json={
                "tittel": tittel,
                "forfatter": forfatter,
                "isbn": isbn,
                "nummer": nummer,
            },
        )
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
