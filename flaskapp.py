from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("kansakri.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]
    password = request.form["password"]
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    email = request.form["email"]
    address = request.form["address"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO users
        (username, password, firstname, lastname, email, address)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, password, firstname, lastname, email, address))

    conn.commit()
    conn.close()

    return redirect(url_for("profile", username=username))


@app.route("/profile/<username>")
def profile(username):

    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    conn.close()

    return render_template("profile.html", user=user, word_count=None)


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()

        conn.close()

        if user:
            return redirect(url_for("profile", username=username))

        return "Invalid username or password"

    return render_template("login.html")


@app.route("/upload/<username>", methods=["POST"])
def upload_file(username):

    file = request.files["file"]

    if file and file.filename:
        
        filename = "Limerick (1).txt"
        upload_folder = "uploads"

        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(upload_folder, filename)

        file.save(filepath)

        with open(filepath, "r") as f:
            text = f.read()

        word_count = len(text.split())

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        return render_template(
            "profile.html",
            user=user,
            word_count=word_count
        )

    return "No file was uploaded"


@app.route("/download")
def download_file():

    return send_from_directory(
        "uploads",
        "Limerick (1).txt",
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)