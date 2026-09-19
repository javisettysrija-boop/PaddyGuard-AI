import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user
)

from dotenv import load_dotenv

from config import Config
from models import db, User


load_dotenv()


app = Flask(__name__)

app.config.from_object(Config)


# Create required folders
os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)

os.makedirs(
    "model",
    exist_ok=True
)


# Initialize database
db.init_app(app)


# Initialize login manager
login_manager = LoginManager()

login_manager.login_view = "login"

login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


# Create database tables
with app.app_context():

    db.create_all()


@app.route("/")
def home():

    if current_user.is_authenticated:

        return redirect(
            url_for("dashboard")
        )

    return redirect(
        url_for("login")
    )


@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form["name"].strip()

        email = request.form["email"].strip().lower()

        password = request.form["password"]

        language = request.form.get(
            "language",
            "en"
        )

        location = request.form.get(
            "location",
            ""
        ).strip()


        if not name or not email or not password:

            flash(
                "Please fill all required fields."
            )

            return redirect(
                url_for("register")
            )


        existing_user = User.query.filter_by(
            email=email
        ).first()


        if existing_user:

            flash(
                "Email already registered."
            )

            return redirect(
                url_for("register")
            )


        user = User(
            name=name,
            email=email,
            language=language,
            location=location
        )

        user.set_password(password)


        db.session.add(user)

        db.session.commit()


        flash(
            "Registration successful. Please login."
        )

        return redirect(
            url_for("login")
        )


    return render_template(
        "register.html"
    )


@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()

        password = request.form["password"]


        user = User.query.filter_by(
            email=email
        ).first()


        if user and user.check_password(password):

            login_user(user)

            return redirect(
                url_for("dashboard")
            )


        flash(
            "Invalid email or password."
        )


    return render_template(
        "login.html"
    )


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )


@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html"
    )


if __name__ == "__main__":

    app.run(
        debug=True
    )