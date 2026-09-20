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

from models import db, User, Diagnosis
from model_utils import predict_image
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)

# --------------------------------------------------
# Configuration
# --------------------------------------------------

app.config["SECRET_KEY"] = "paddyguard-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///paddyguard.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["UPLOAD_FOLDER"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "uploads"
)

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)


# --------------------------------------------------
# Database
# --------------------------------------------------

db.init_app(app)


# --------------------------------------------------
# Flask Login
# --------------------------------------------------

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --------------------------------------------------
# Create database tables
# --------------------------------------------------

with app.app_context():
    db.create_all()


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.route("/")
def home():
    return redirect(url_for("dashboard"))


# --------------------------------------------------
# Register
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            flash("Please fill all fields.")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            flash("Email already registered.")
            return redirect(url_for("register"))

        user = User(
            name=name,
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.")

        return redirect(url_for("login"))

    return render_template("register.html")


# --------------------------------------------------
# Login
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.check_password(password):

            login_user(user)

            return redirect(
                url_for("dashboard")
            )

        flash("Invalid email or password.")

    return render_template("login.html")


# --------------------------------------------------
# Logout
# --------------------------------------------------

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )


# --------------------------------------------------
# Dashboard
# --------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html"
    )


# --------------------------------------------------
# Disease Detection / Upload
# --------------------------------------------------

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files.get("image")

        if not file or not file.filename:
            flash("Please choose a paddy leaf image.")
            return redirect(url_for("upload"))

        allowed = {"jpg", "jpeg", "png"}

        if "." not in file.filename:
            flash("Invalid file.")
            return redirect(url_for("upload"))

        ext = file.filename.rsplit(".", 1)[1].lower()

        if ext not in allowed:
            flash("Only JPG, JPEG and PNG images are allowed.")
            return redirect(url_for("upload"))

        filename = secure_filename(file.filename)
        filename = f"{current_user.id}_{filename}"

        path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(path)

        try:
            disease, confidence = predict_image(path)

        except Exception:
            app.logger.exception("Prediction failed")

            flash(
                "AI prediction failed. Check that the model exists."
            )

            return redirect(url_for("upload"))

        diagnosis = Diagnosis(
            user_id=current_user.id,
            image_name=filename,
            disease=disease,
            confidence=confidence
        )

        db.session.add(diagnosis)
        db.session.commit()

        return render_template(
            "result.html",
            disease=disease,
            confidence=round(confidence, 2)
        )

    return render_template("upload.html")


# --------------------------------------------------
# Diagnosis History
# --------------------------------------------------

@app.route("/history")
@login_required
def history():
    diagnoses = Diagnosis.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Diagnosis.created_at.desc()
    ).all()

    return render_template(
        "history.html",
        diagnoses=diagnoses
    )

# --------------------------------------------------
# Run Application
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )