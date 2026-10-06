from flask import Flask, render_template, request, redirect, session
import random
import mysql.connector

app = Flask(__name__)
app.secret_key = "library123"


# DATABASE
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="library_db"
)

cursor = db.cursor()


# LOGIN
@app.route("/", methods=["GET", "POST"])
def login():

    if "captcha" not in session:
        session["captcha"] = random.randint(1000, 9999)

    message = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        captcha = request.form["captcha"]

        if username == "admin" and password == "admin123" and captcha == str(session["captcha"]):

            session["login"] = True

            return redirect("/dashboard")

        else:

            message = "Invalid Username, Password or CAPTCHA"

            session["captcha"] = random.randint(1000, 9999)

    return render_template(
        "login.html",
        captcha=session["captcha"],
        message=message
    )


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "login" not in session:
        return redirect("/")

    cursor.execute("SELECT COUNT(*) FROM books")

    total = cursor.fetchone()[0]

    return render_template(
        "dashboard.html",
        total=total
    )


# VIEW BOOKS
@app.route("/books")
def books():

    if "login" not in session:
        return redirect("/")

    cursor.execute("SELECT id, book_id, title, author, category FROM books")

    book_list = cursor.fetchall()

    return render_template(
        "books.html",
        books=book_list
    )


# ADD BOOK
@app.route("/add", methods=["GET", "POST"])
def add_book():

    if "login" not in session:
        return redirect("/")

    if request.method == "POST":

        book_id = request.form["book_id"]
        title = request.form["title"]
        author = request.form["author"]
        category = request.form["category"]

        cursor.execute(
            """
            INSERT INTO books
            (book_id, title, author, category)
            VALUES (%s, %s, %s, %s)
            """,
            (book_id, title, author, category)
        )

        db.commit()

        return redirect("/books")

    return render_template("add_book.html")


# EDIT BOOK
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_book(id):

    if "login" not in session:
        return redirect("/")

    if request.method == "POST":

        book_id = request.form["book_id"]
        title = request.form["title"]
        author = request.form["author"]
        category = request.form["category"]

        cursor.execute(
            """
            UPDATE books
            SET book_id=%s,
                title=%s,
                author=%s,
                category=%s
            WHERE id=%s
            """,
            (book_id, title, author, category, id)
        )

        db.commit()

        return redirect("/books")

    cursor.execute(
        "SELECT id, book_id, title, author, category FROM books WHERE id=%s",
        (id,)
    )

    book = cursor.fetchone()

    return render_template(
        "edit_book.html",
        book=book
    )


# DELETE BOOK
@app.route("/delete/<int:id>")
def delete_book(id):

    if "login" not in session:
        return redirect("/")

    cursor.execute(
        "DELETE FROM books WHERE id=%s",
        (id,)
    )

    db.commit()

    return redirect("/books")


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)