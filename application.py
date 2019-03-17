import os

from flask import Flask, redirect, session, url_for, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if 'username' in session:
        username = session['username']
        session['logged_in'] = True
        return render_template("index.html")
    else:
        return render_template("login.html")

@app.route("/search", methods = ["GET", "POST"])
def search():
    if request.method == "POST":
        req = request.form.get("req")
        req = '%' + req + '%'
        results = db.execute("SELECT * FROM books WHERE isbn ILIKE :req OR title ILIKE :req OR author ILIKE :req", {"req": req}).fetchall()
        # if books is None:
        #     return render_template('error.html', message = "result not found")
        # result = True
        return render_template("search.html", results = results)
    return render_template("search.html")

@app.route("/result/<book>")
def result(book):
    bookresult = db.execute("SELECT * FROM books WHERE title = :title", {"title": book}).fetchone()
    # bookID = db.execute("SELECT id FROM books WHERE title = :title", {"title": book}).fetchone()
    reviews = db.execute("SELECT * FROM reviews JOIN users ON users.id = reviews.user_id WHERE book_id = (SELECT id FROM books WHERE title = :title)", {"title": book}).fetchall()
    return render_template("result.html", bookresult = bookresult, reviews = reviews)


@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        users = db.execute("SELECT * FROM users").fetchall()
        username = request.form.get("username")
        password = request.form.get("password")

        if db.execute("SELECT * FROM users WHERE username = :username AND password = :password",
            {"username": username, "password": password}).rowcount == 0:
            return render_template('login.html', message = "Username or password is incorrect. Please try again.")
        else:
            session['username'] = username
            session['logged_in'] = True
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/signup", methods = ["GET", "POST"])
def signup():
    if request.method == "POST":
        users = db.execute("SELECT * FROM users").fetchall()

        username = request.form.get("username")
        password = request.form.get("password")
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": password})
            db.commit()
            return redirect(url_for('index'))
        else:
            message = "That username already exists. Please try again"
            return render_template("signup.html", message = message)
    return render_template("signup.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for("login"))
