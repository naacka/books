import os

from flask import Flask, session, render_template, request
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
    users = db.execute("SELECT * FROM users").fetchall()
    return render_template("index.html", users=users)

@app.route("/signin", methods=["POST"])
def signin():
    users = db.execute("SELECT * FROM users").fetchall()
    username = request.form.get("username")
    password = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password",
        {"username": username, "password": password}).rowcount == 0:
        return render_template("error.html", message="Username or password is incorrect.")
    else:
        return render_template("signin.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/thanks", methods=["POST"])
def thanks():
    users = db.execute("SELECT * FROM users").fetchall()

    username = request.form.get("username")
    password = request.form.get("password")
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": password})
        db.commit()
    else:
        render_template("error.html", message="That username already exists. Please try again")

    return render_template("thanks.html")
