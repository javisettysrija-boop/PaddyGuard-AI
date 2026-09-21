import os
import sqlite3

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import generate_password_hash, check_password_hash

from model_utils import predict_disease


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

# Secret key is required for Flask session
app.secret_key = "paddyguard_secret_key"


# ============================================================
# CONFIGURATION
# ============================================================

DATABASE = "database.db"

UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB


# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_database():

    conn = get_db_connection()

    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Prediction history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT,
            disease TEXT,
            confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# Initialize database
init_database()


# ============================================================
# HELPER FUNCTION - CHECK ALLOWED FILE
# ============================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ============================================================
# HOME / PREDICTION PAGE
# ============================================================

@app.route("/", methods=["GET", "POST"])
def index():

    # --------------------------------------------------------
    # GET REQUEST
    # --------------------------------------------------------

    if request.method == "GET":

        return render_template("index.html")


    # --------------------------------------------------------
    # POST REQUEST
    # --------------------------------------------------------

    if "user_id" not in session:
        return redirect(url_for("login"))


    # Check whether file exists

    if "file" not in request.files:

        return render_template(
            "index.html",
            error="Please select a paddy leaf image."
        )


    file = request.files["file"]


    # Check filename

    if file.filename == "":

        return render_template(
            "index.html",
            error="Please select an image."
        )


    # Check file type

    if not allowed_file(file.filename):

        return render_template(
            "index.html",
            error="Invalid file type. Please upload JPG, JPEG, PNG or WEBP."
        )


    # --------------------------------------------------------
    # SAVE IMAGE
    # --------------------------------------------------------

    filename = file.filename

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(filepath)


    # --------------------------------------------------------
    # AI PREDICTION
    # --------------------------------------------------------

    try:

        disease, confidence = predict_disease(filepath)

    except Exception as e:

        print("Prediction error:", e)

        return render_template(
            "index.html",
            error="Unable to process the image. Please try another image."
        )


    # --------------------------------------------------------
    # SAVE PREDICTION TO DATABASE
    # --------------------------------------------------------

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO predictions
        (user_id, filename, disease, confidence)
        VALUES (?, ?, ?, ?)
        """,
        (
            session["user_id"],
            filename,
            disease,
            confidence
        )
    )

    conn.commit()
    conn.close()


    # --------------------------------------------------------
    # RESULT PAGE
    # --------------------------------------------------------

    return render_template(
        "result.html",
        disease=disease,
        confidence=confidence,
        filename=filename
    )


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    # Show registration page

    if request.method == "GET":

        return render_template("register.html")


    # --------------------------------------------------------
    # GET FORM DATA
    # --------------------------------------------------------

    name = request.form.get("name", "").strip()

    email = request.form.get("email", "").strip().lower()

    password = request.form.get("password", "")


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not name or not email or not password:

        return render_template(
            "register.html",
            error="All fields are required."
        )


    if len(password) < 6:

        return render_template(
            "register.html",
            error="Password must contain at least 6 characters."
        )


    # --------------------------------------------------------
    # HASH PASSWORD
    # --------------------------------------------------------

    hashed_password = generate_password_hash(password)


    # --------------------------------------------------------
    # INSERT USER
    # --------------------------------------------------------

    conn = get_db_connection()

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password)
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                hashed_password
            )
        )

        conn.commit()

    except sqlite3.IntegrityError:

        conn.close()

        return render_template(
            "register.html",
            error="This email is already registered."
        )

    conn.close()


    # Registration successful

    return redirect(url_for("login"))


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # Show login page

    if request.method == "GET":

        return render_template("login.html")


    # --------------------------------------------------------
    # GET LOGIN DETAILS
    # --------------------------------------------------------

    email = request.form.get("email", "").strip().lower()

    password = request.form.get("password", "")


    if not email or not password:

        return render_template(
            "login.html",
            error="Email and password are required."
        )


    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, email, password
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    conn.close()


    # --------------------------------------------------------
    # CHECK PASSWORD
    # --------------------------------------------------------

    if user and check_password_hash(
        user["password"],
        password
    ):

        # Store login information in session

        session["user_id"] = user["id"]

        session["user_name"] = user["name"]

        session["user_email"] = user["email"]


        return redirect(url_for("dashboard"))


    # Invalid login

    return render_template(
        "login.html",
        error="Invalid email or password."
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    if "user_id" not in session:

        return redirect(url_for("login"))


    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    return render_template(
        "dashboard.html"
    )


# ============================================================
# PREDICTION HISTORY
# ============================================================

@app.route("/history")
def history():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    if "user_id" not in session:

        return redirect(url_for("login"))


    # --------------------------------------------------------
    # GET ONLY CURRENT USER'S HISTORY
    # --------------------------------------------------------

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            disease,
            confidence,
            created_at,
            filename
        FROM predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    )

    history_data = cursor.fetchall()

    conn.close()


    # --------------------------------------------------------
    # SEND TO TEMPLATE
    # --------------------------------------------------------

    return render_template(
        "history.html",
        history=history_data
    )


# ============================================================
# DISEASE INFORMATION
# ============================================================

@app.route("/diseases")
def diseases():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    if "user_id" not in session:

        return redirect(url_for("login"))


    # --------------------------------------------------------
    # PADDY DISEASE INFORMATION
    # --------------------------------------------------------

    diseases_data = [

        {
            "name": "Bacterial Leaf Blight",
            "symptoms":
                "Water-soaked lesions appear on leaf margins. "
                "Leaves may turn yellow and dry.",
            "cause":
                "Caused by bacterial infection.",
            "prevention":
                "Use healthy planting material, maintain field sanitation "
                "and avoid excessive nitrogen.",
            "treatment":
                "Follow locally recommended bacterial disease-management "
                "practices."
        },

        {
            "name": "Brown Spot",
            "symptoms":
                "Brown circular or oval spots appear on leaves.",
            "cause":
                "Caused by a fungal pathogen.",
            "prevention":
                "Maintain balanced crop nutrition and good field hygiene.",
            "treatment":
                "Use locally recommended fungicide and crop-management "
                "practices."
        },

        {
            "name": "Leaf Blast",
            "symptoms":
                "Spindle-shaped spots with gray centers may appear on leaves.",
            "cause":
                "Caused by a fungal pathogen.",
            "prevention":
                "Avoid excessive nitrogen and maintain proper field management.",
            "treatment":
                "Follow locally recommended blast-management practices."
        },

        {
            "name": "Neck Blast",
            "symptoms":
                "Dark lesions develop around the neck of the panicle.",
            "cause":
                "Fungal infection affecting the panicle neck.",
            "prevention":
                "Use balanced fertilizer application and monitor the crop.",
            "treatment":
                "Use locally recommended disease-management practices."
        },

        {
            "name": "Tungro",
            "symptoms":
                "Plants may show yellow-orange discoloration and stunted growth.",
            "cause":
                "Viral disease transmitted by insect vectors.",
            "prevention":
                "Monitor vector populations and remove infected plants "
                "according to local recommendations.",
            "treatment":
                "Follow locally recommended vector and disease-management "
                "practices."
        },

        {
            "name": "Sheath Blight",
            "symptoms":
                "Oval greenish-gray lesions appear on leaf sheaths.",
            "cause":
                "Caused by a fungal pathogen.",
            "prevention":
                "Avoid excessive nitrogen and maintain suitable plant spacing.",
            "treatment":
                "Follow locally recommended sheath-blight management."
        },

        {
            "name": "Hispa",
            "symptoms":
                "Leaves show scraped or white streak-like damage.",
            "cause":
                "Caused by rice hispa insect feeding.",
            "prevention":
                "Regularly monitor the crop for insect activity.",
            "treatment":
                "Follow locally recommended integrated pest-management "
                "practices."
        },

        {
            "name": "Leaf Folder",
            "symptoms":
                "Leaves become folded and show feeding damage.",
            "cause":
                "Caused by leaf-folder insect larvae.",
            "prevention":
                "Regularly inspect folded leaves and monitor pest levels.",
            "treatment":
                "Use locally recommended integrated pest-management methods."
        },

        {
            "name": "Healthy",
            "symptoms":
                "Leaves appear green and show no major disease symptoms.",
            "cause":
                "No major disease detected.",
            "prevention":
                "Continue good crop management and regular monitoring.",
            "treatment":
                "No disease treatment is required."
        },

        {
            "name": "Rice Stem Borer",
            "symptoms":
                "Plants may show dead hearts or white heads.",
            "cause":
                "Damage caused by stem-borer larvae.",
            "prevention":
                "Monitor fields regularly and follow integrated pest-management "
                "practices.",
            "treatment":
                "Use locally recommended pest-management practices."
        }

    ]


    return render_template(
        "diseases.html",
        diseases=diseases_data
    )


# ============================================================
# WEATHER
# ============================================================

@app.route("/weather")
def weather():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    if "user_id" not in session:

        return redirect(url_for("login"))


    # --------------------------------------------------------
    # TEMPORARY WEATHER VALUES
    # --------------------------------------------------------
    #
    # These are placeholders.
    # Later Member 1 can connect a weather API.
    #

    temperature = None

    humidity = None

    rainfall = None


    return render_template(
        "weather.html",
        temperature=temperature,
        humidity=humidity,
        rainfall=rainfall
    )


# ============================================================
# CROP ALERT FUNCTION
# ============================================================

def generate_alert(
    temperature=None,
    humidity=None,
    rainfall=None
):

    alerts = []


    if temperature is not None:

        if temperature > 35:

            alerts.append(
                "High temperature alert. "
                "Monitor the paddy crop regularly."
            )


    if humidity is not None:

        if humidity > 85:

            alerts.append(
                "High humidity alert. "
                "Monitor the crop for fungal diseases."
            )


    if rainfall is not None:

        if rainfall > 50:

            alerts.append(
                "Heavy rainfall alert. "
                "Check field drainage."
            )


    return alerts


# ============================================================
# CROP ALERTS
# ============================================================

@app.route("/alerts")
def alerts():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    if "user_id" not in session:

        return redirect(url_for("login"))


    # --------------------------------------------------------
    # TEMPORARY VALUES
    # --------------------------------------------------------
    #
    # Later these values can come from weather API.
    #

    temperature = None

    humidity = None

    rainfall = None


    # Generate alerts

    alerts_data = generate_alert(
        temperature,
        humidity,
        rainfall
    )


    return render_template(
        "alerts.html",
        alerts=alerts_data
    )


# ============================================================
# ERROR HANDLER - FILE TOO LARGE
# ============================================================

@app.errorhandler(413)
def request_entity_too_large(error):

    return render_template(
        "index.html",
        error="File is too large. Maximum size is 10 MB."
    ), 413


# ============================================================
# ERROR HANDLER - PAGE NOT FOUND
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <h1>404 - Page Not Found</h1>
    <p>The requested page does not exist.</p>
    """, 404


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )