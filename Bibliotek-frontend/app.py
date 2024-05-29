from flask import Flask, render_template, request, redirect
import requests
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def index():
    response = requests.get("http://192.168.10.27/")
    if response.status_code == 500:
        return render_template(
            "error.html", error=response.json()["error"], status=response.status_code
        )
    return render_template("index.html", bøker=response.json())


@app.route("/bok/<int:nummer>", methods=["GET"])
def bok(nummer):
    if nummer == 0:
        nummer = request.args.get("nummer")
    if int(nummer) < 1 or int(nummer) > 51:
        return render_template(
            "error.html", error="Bok nummer utenfor rekkevidden", status=404
        )
    response = requests.get("http://192.168.10.27/bok/" + str(nummer))
    if response.status_code == 500 or response.status_code == 404:
        return render_template(
            "error.html", error=response.json()["error"], status=response.status_code
        )
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
    if not streng:
        return redirect("/")
    response = requests.get("http://192.168.10.27:/filter/" + streng)
    if response.status_code == 500:
        return render_template(
            "error.html", error=response.json()["error"], status=response.status_code
        )
    if response.status_code == 404:
        return render_template(
            "index.html", error=response.json()["error"], streng=streng
        )
    return render_template("index.html", bøker=response.json(), streng=streng)


@app.route("/slettbok/<nummer>", methods=["POST"])
def slettbok(nummer):
    response = requests.delete("http://192.168.10.27:/slettbok/" + nummer)
    if response.status_code == 500 or response.status_code == 404:
        return render_template(
            "error.html", error=response.json()["error"], status=response.status_code
        )
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
        if nummer == "":
            nummer = 0
        response = requests.post(
            "http://192.168.10.27:/leggtilbok",
            json={
                "tittel": tittel,
                "forfatter": forfatter,
                "isbn": isbn,
                "nummer": nummer,
            },
        )
        if response.status_code == 500 or response.status_code == 409:
            return render_template(
                "error.html",
                error=response.json()["error"],
                status=response.status_code,
            )
        return redirect("/")


@app.route("/registrer", methods=["GET", "POST"])
def registrer():
    if request.method == "GET":
        return render_template("registrer.html")

    if request.method == "POST":
        fornavn = request.form.get("fornavn")
        etternavn = request.form.get("etternavn")
        nummer = request.form.get("nummer")
        requests.post(
            "http://192.168.10.27/registrer",
            json={"fornavn": fornavn, "etternavn": etternavn, "nummer": nummer},
        )
        return redirect("/")


@app.route("/brukere", methods=["GET"])
def brukere():
    response = requests.get("http://192.168.10.27/brukere")
    return render_template("brukere.html", brukere=response.json())


@app.route("/bruker/<nummer>", methods=["GET"])
def bruker(nummer):
    response = requests.get("http://192.168.10.27/bruker", json={"nummer": nummer})
    return render_template("bruker.html", bruker=response.json())


@app.route("/lån_bruker", methods=["POST"])
def lån_bruker():
    nummer = request.form.get("nummer")
    response = requests.get("http://192.168.10.27/bruker", json={"nummer": nummer})
    return render_template("lån_bok.html", bruker=response.json())


@app.route("/lån_bok>", methods=["GET", "POST"])
def lån_bok():
    if request.method == "GET":
        return render_template("lån_bok.html")

    if request.method == "POST":
        bruker_id = request.form.get("bruker_id")
        bok_id = request.form.get("bok_id")
        requests.post(
            "http://192.168.10.27/lån_bok",
            json={"bok_id": bok_id, "bruker_id": bruker_id},
        )
        return redirect("/")


@app.route("/hent_bok", methods=["GET"])
def hent_bok():
    nummer = request.args.get("nummer")
    bruker_id = request.args.get("bruker_id")
    bruker = requests.get(
        "http://192.168.10.27/bruker", json={"nummer": bruker_id}
    ).json()
    response = requests.get("http://192.168.10.27/bok/" + str(nummer))
    if response.status_code == 500 or response.status_code == 404:
        return render_template(
            "error.html", error=response.json()["error"], status=response.status_code
        )
    return render_template("lån_bok.html", bruker=bruker, bok=response.json())


@app.route("/lever_bok", methods=["GET", "POST"])
def lever_bok():
    if request.method == "GET":
        return render_template("lever_bok.html")

    if request.method == "POST":
        bok_id = request.form.get("bok_id")
        requests.post("http://192.168.10.27/lever_bok", json={"bok_id": bok_id})
        return redirect("/")


@app.route("/aktive_lånere", methods=["GET"])
def aktive_lånere():
    response = requests.get("http://192.168.10.27/aktive_lånere")
    return render_template(
        "aktive_lånere.html", bøker=response.json()[0], brukere=response.json()[1]
    )


if __name__ == "__main__":
    app.run(debug=True)
