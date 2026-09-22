import os
import sqlite3
import urllib.request
import urllib.parse
import json

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

# ============================================================
# AI MODEL
# ============================================================

from model_utils import predict_image


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "paddyguard_secret_key"
)


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# CONFIGURATION
# ============================================================

DATABASE = os.path.join(
    BASE_DIR,
    "database.db"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

CLASSES_FILE = os.path.join(
    BASE_DIR,
    "classes.txt"
)

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Maximum upload size = 10 MB
app.config["MAX_CONTENT_LENGTH"] = (
    10 * 1024 * 1024
)

# Create upload folder
os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():

    conn = sqlite3.connect(
        DATABASE
    )

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_database():

    conn = get_db_connection()

    cursor = conn.cursor()

    # --------------------------------------------------------
    # USERS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # PREDICTIONS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            filename TEXT,

            disease TEXT,

            confidence REAL,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)

    conn.commit()

    conn.close()


# Initialize database
init_database()


# ============================================================
# HELPER - LOGIN REQUIRED
# ============================================================

def login_required():

    if "user_id" not in session:

        return False

    return True


# ============================================================
# HELPER - ALLOWED FILE
# ============================================================

def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# HELPER - LOAD MODEL CLASSES
# ============================================================

def load_classes():

    classes = []

    try:

        if os.path.exists(
            CLASSES_FILE
        ):

            with open(
                CLASSES_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                for line in file:

                    name = line.strip()

                    if name:

                        classes.append(
                            name
                        )

    except Exception as e:

        print(
            "Unable to read classes.txt:",
            e
        )

    return classes


# ============================================================
# DISEASE INFORMATION
# ============================================================

DISEASE_INFO = {

    "Bacterial Leaf Blight": {
        "symptoms":
            "Water-soaked lesions may appear "
            "along leaf margins. Leaves can turn "
            "yellow and dry.",

        "cause":
            "A bacterial disease affecting rice plants.",

        "prevention":
            "Use healthy planting material, "
            "maintain field sanitation and avoid "
            "excessive nitrogen.",

        "treatment":
            "Follow locally recommended bacterial "
            "disease-management practices."
    },

    "Brown Spot": {
        "symptoms":
            "Brown circular or oval spots may "
            "appear on rice leaves.",

        "cause":
            "A fungal disease that can be associated "
            "with crop stress and nutrient imbalance.",

        "prevention":
            "Maintain balanced crop nutrition, "
            "good field hygiene and proper crop care.",

        "treatment":
            "Follow locally recommended fungicide "
            "and crop-management practices."
    },

    "Leaf Blast": {
        "symptoms":
            "Spindle-shaped lesions with grayish "
            "centers may appear on leaves.",

        "cause":
            "A fungal disease affecting rice leaves.",

        "prevention":
            "Avoid excessive nitrogen and maintain "
            "proper crop and field management.",

        "treatment":
            "Follow locally recommended rice blast "
            "management practices."
    },

    "Neck Blast": {
        "symptoms":
            "Dark lesions may develop around the "
            "neck of the rice panicle.",

        "cause":
            "A fungal disease affecting the panicle neck.",

        "prevention":
            "Use balanced fertilizer application "
            "and regularly monitor the crop.",

        "treatment":
            "Follow locally recommended blast "
            "management practices."
    },

    "Tungro": {
        "symptoms":
            "Plants may show yellow to orange "
            "discoloration and stunted growth.",

        "cause":
            "A viral rice disease transmitted by "
            "insect vectors.",

        "prevention":
            "Monitor insect vectors and follow "
            "recommended field sanitation practices.",

        "treatment":
            "Follow locally recommended vector "
            "and disease-management practices."
    },

    "Sheath Blight": {
        "symptoms":
            "Oval greenish-gray lesions may appear "
            "on leaf sheaths.",

        "cause":
            "A fungal disease affecting rice sheaths.",

        "prevention":
            "Avoid excessive nitrogen and maintain "
            "appropriate crop density and field management.",

        "treatment":
            "Follow locally recommended sheath-blight "
            "management practices."
    },

    "Hispa": {
        "symptoms":
            "Leaves may show scraped or damaged "
            "areas caused by insect feeding.",

        "cause":
            "Rice hispa insect infestation.",

        "prevention":
            "Regularly monitor the crop for insect "
            "activity and maintain field sanitation.",

        "treatment":
            "Follow locally recommended pest-management "
            "practices."
    },

    "Rice Hispa": {
        "symptoms":
            "Rice leaves may develop scraped or "
            "whitish damaged areas.",

        "cause":
            "Damage caused by rice hispa insects.",

        "prevention":
            "Regularly inspect plants and use "
            "recommended pest-management practices.",

        "treatment":
            "Follow locally recommended pest-control "
            "measures."
    },

    "Dead Heart": {
        "symptoms":
            "Young rice shoots may dry and become "
            "dead while the central shoot can be "
            "easily pulled out.",

        "cause":
            "Commonly associated with stem-boring insect damage.",

        "prevention":
            "Monitor the crop regularly for stem "
            "borer activity.",

        "treatment":
            "Follow locally recommended integrated "
            "pest-management practices."
    },

    "Hispa": {
        "symptoms":
            "Leaves can show white scraped areas "
            "caused by insect feeding.",

        "cause":
            "Rice hispa infestation.",

        "prevention":
            "Monitor fields regularly and maintain "
            "proper crop management.",

        "treatment":
            "Use locally recommended pest-management "
            "practices."
    }
}


# ============================================================
# HELPER - GET DISEASE INFORMATION
# ============================================================

def get_disease_info(disease):

    if not disease:

        return {
            "symptoms": "No information available.",
            "cause": "No information available.",
            "prevention": "Please consult a local agricultural expert.",
            "treatment": "Please consult a local agricultural expert."
        }

    # Exact match
    if disease in DISEASE_INFO:

        return DISEASE_INFO[disease]

    # Case-insensitive match
    disease_lower = disease.lower()

    for name, info in DISEASE_INFO.items():

        if name.lower() == disease_lower:

            return info

    # Partial match
    for name, info in DISEASE_INFO.items():

        if (
            name.lower() in disease_lower
            or
            disease_lower in name.lower()
        ):

            return info

    # Generic fallback
    return {
        "symptoms":
            "The AI model detected this class "
            "from the uploaded paddy image.",

        "cause":
            "The exact cause should be confirmed "
            "with an agricultural expert.",

        "prevention":
            "Monitor the crop regularly and maintain "
            "good field hygiene and balanced nutrition.",

        "treatment":
            "Follow locally recommended crop-management "
            "practices after confirming the diagnosis."
    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    if "user_id" in session:

        return redirect(
            url_for("dashboard")
        )

    return redirect(
        url_for("login")
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "GET":

        return render_template(
            "register.html"
        )

    # --------------------------------------------------------
    # FORM DATA
    # --------------------------------------------------------

    name = request.form.get(
        "name",
        ""
    ).strip()

    # Support username field
    if not name:

        name = request.form.get(
            "username",
            ""
        ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not name:

        return render_template(
            "register.html",
            error="Name is required."
        )

    if not email:

        return render_template(
            "register.html",
            error="Email is required."
        )

    if not password:

        return render_template(
            "register.html",
            error="Password is required."
        )

    if len(password) < 6:

        return render_template(
            "register.html",
            error=(
                "Password must contain "
                "at least 6 characters."
            )
        )

    if (
        confirm_password
        and
        password != confirm_password
    ):

        return render_template(
            "register.html",
            error="Passwords do not match."
        )

    # --------------------------------------------------------
    # HASH PASSWORD
    # --------------------------------------------------------

    hashed_password = generate_password_hash(
        password
    )

    # --------------------------------------------------------
    # SAVE USER
    # --------------------------------------------------------

    conn = get_db_connection()

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password
            )
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
            error=(
                "This email is already registered."
            )
        )

    conn.close()

    flash(
        "Registration successful. Please login.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "GET":

        return render_template(
            "login.html"
        )

    # --------------------------------------------------------
    # FORM DATA
    # --------------------------------------------------------

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    # Support username field
    if not email and username:

        email = username.lower()

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not email or not password:

        return render_template(
            "login.html",
            error=(
                "Email and password "
                "are required."
            )
        )

    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            password
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

    if user:

        try:

            password_valid = check_password_hash(
                user["password"],
                password
            )

        except Exception:

            password_valid = False

        if password_valid:

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            session["user_email"] = user["email"]

            flash(
                "Login successful.",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

    # --------------------------------------------------------
    # INVALID LOGIN
    # --------------------------------------------------------

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

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if not login_required():

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    cursor = conn.cursor()

    # Total predictions
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM predictions
        WHERE user_id = ?
        """,
        (
            session["user_id"],
        )
    )

    result = cursor.fetchone()

    total_predictions = result["total"]

    # Recent predictions
    cursor.execute(
        """
        SELECT
            disease,
            confidence,
            created_at,
            filename
        FROM predictions
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
        """,
        (
            session["user_id"],
        )
    )

    recent_predictions = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_predictions=total_predictions,
        recent_predictions=recent_predictions
    )


# ============================================================
# UPLOAD / AI PREDICTION
# ============================================================

@app.route(
    "/upload",
    methods=["GET", "POST"]
)
def upload():

    if not login_required():

        return redirect(
            url_for("login")
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    if request.method == "GET":

        return render_template(
            "upload.html"
        )

    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if "file" not in request.files:

        return render_template(
            "upload.html",
            error=(
                "Please select a paddy leaf image."
            )
        )

    file = request.files["file"]

    if file.filename == "":

        return render_template(
            "upload.html",
            error="Please select an image."
        )

    # --------------------------------------------------------
    # FILE TYPE
    # --------------------------------------------------------

    if not allowed_file(
        file.filename
    ):

        return render_template(
            "upload.html",
            error=(
                "Invalid file type. "
                "Please upload JPG, JPEG, PNG or WEBP."
            )
        )

    # --------------------------------------------------------
    # SECURE FILENAME
    # --------------------------------------------------------

    original_filename = secure_filename(
        file.filename
    )

    if not original_filename:

        return render_template(
            "upload.html",
            error="Invalid filename."
        )

    # --------------------------------------------------------
    # CREATE UNIQUE FILENAME
    # --------------------------------------------------------

    import time

    filename = (
        str(int(time.time()))
        + "_"
        + original_filename
    )

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    # --------------------------------------------------------
    # SAVE IMAGE
    # --------------------------------------------------------

    try:

        file.save(
            filepath
        )

    except Exception as e:

        print(
            "File save error:",
            e
        )

        return render_template(
            "upload.html",
            error=(
                "Unable to save the uploaded image."
            )
        )

    # --------------------------------------------------------
    # AI PREDICTION
    # --------------------------------------------------------

    try:

        result = predict_image(
            filepath
        )

        # model_utils.py is expected to return:
        #
        # disease, confidence

        disease, confidence = result

        # Convert confidence to float
        confidence = float(
            confidence
        )

    except Exception as e:

        print(
            "Prediction error:",
            e
        )

        try:

            if os.path.exists(
                filepath
            ):

                os.remove(
                    filepath
                )

        except Exception:

            pass

        return render_template(
            "upload.html",
            error=(
                "Unable to process the image. "
                "Please try another paddy leaf image."
            )
        )

    # --------------------------------------------------------
    # DISEASE INFORMATION
    # --------------------------------------------------------

    disease_info = get_disease_info(
        disease
    )

    farmer_warning = (
        "AI prediction is for assistance only. "
        "Please confirm the disease with a "
        "qualified agricultural expert before "
        "applying treatment."
    )

    # --------------------------------------------------------
    # SAVE HISTORY
    # --------------------------------------------------------

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO predictions
        (
            user_id,
            filename,
            disease,
            confidence
        )
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

        prediction=disease,

        disease=disease,

        confidence=confidence,

        filename=filename,

        disease_info=disease_info,

        farmer_warning=farmer_warning
    )


# ============================================================
# HISTORY
# ============================================================

@app.route("/history")
def history():

    if not login_required():

        return redirect(
            url_for("login")
        )

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
        ORDER BY id DESC
        """,
        (
            session["user_id"],
        )
    )

    history_data = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        history=history_data
    )


# ============================================================
# DISEASES
# ============================================================

@app.route("/diseases")
def diseases():

    if not login_required():

        return redirect(
            url_for("login")
        )

    # Load actual model classes if classes.txt exists
    model_classes = load_classes()

    diseases_data = []

    # Use actual classes.txt names
    if model_classes:

        for disease_name in model_classes:

            info = get_disease_info(
                disease_name
            )

            diseases_data.append(
                {
                    "name": disease_name,
                    "symptoms": info["symptoms"],
                    "cause": info["cause"],
                    "prevention": info["prevention"],
                    "treatment": info["treatment"]
                }
            )

    else:

        # Fallback to available disease information
        for disease_name, info in DISEASE_INFO.items():

            diseases_data.append(
                {
                    "name": disease_name,
                    "symptoms": info["symptoms"],
                    "cause": info["cause"],
                    "prevention": info["prevention"],
                    "treatment": info["treatment"]
                }
            )

    return render_template(
        "diseases.html",
        diseases=diseases_data
    )


# ============================================================
# WEATHER
# ============================================================

@app.route("/weather")
def weather():

    if not login_required():

        return redirect(
            url_for("login")
        )

    # --------------------------------------------------------
    # DEFAULT WEATHER VALUES
    # --------------------------------------------------------

    temperature = "--"

    humidity = "--"

    rainfall = "--"

    weather_description = (
        "Weather information is currently unavailable."
    )

    city = "Andhra Pradesh"

    # --------------------------------------------------------
    # OPTIONAL OPENWEATHER API
    # --------------------------------------------------------

    api_key = os.environ.get(
        "OPENWEATHER_API_KEY"
    )

    if api_key:

        try:

            query = urllib.parse.quote(
                "Andhra Pradesh,IN"
            )

            url = (
                "https://api.openweathermap.org/data/2.5/weather"
                "?q="
                + query
                + "&appid="
                + api_key
                + "&units=metric"
            )

            with urllib.request.urlopen(
                url,
                timeout=5
            ) as response:

                data = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

            temperature = round(
                data["main"]["temp"],
                1
            )

            humidity = data["main"]["humidity"]

            weather_description = (
                data["weather"][0]["description"]
                .title()
            )

            city = data.get(
                "name",
                "Andhra Pradesh"
            )

            # OpenWeather rain data
            rainfall = 0

            if "rain" in data:

                if "1h" in data["rain"]:

                    rainfall = data["rain"]["1h"]

                elif "3h" in data["rain"]:

                    rainfall = data["rain"]["3h"]

        except Exception as e:

            print(
                "Weather API error:",
                e
            )

    # --------------------------------------------------------
    # WEATHER PAGE
    # --------------------------------------------------------

    return render_template(
        "weather.html",

        temperature=temperature,

        humidity=humidity,

        rainfall=rainfall,

        weather_description=weather_description,

        city=city
    )


# ============================================================
# CROP ALERTS
# ============================================================

@app.route("/alerts")
def alerts():

    if not login_required():

        return redirect(
            url_for("login")
        )

    alerts_data = [

        {
            "title":
                "Monitor Paddy Leaves",

            "message":
                "Regularly inspect paddy leaves "
                "for spots, discoloration and unusual "
                "growth.",

            "type":
                "info"
        },

        {
            "title":
                "Check Field Water",

            "message":
                "Maintain suitable water management "
                "according to the current growth stage "
                "of the paddy crop.",

            "type":
                "warning"
        },

        {
            "title":
                "Watch for Pests",

            "message":
                "Check the crop regularly for insect "
                "damage and follow integrated pest "
                "management practices.",

            "type":
                "warning"
        },

        {
            "title":
                "Disease Detection",

            "message":
                "Upload a clear paddy leaf image "
                "to use PaddyGuard AI disease detection.",

            "type":
                "success"
        }
    ]

    return render_template(
        "alerts.html",
        alerts=alerts_data
    )


# ============================================================
# PROFILE
# ============================================================

@app.route("/profile")
def profile():

    if not login_required():

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email
        FROM users
        WHERE id = ?
        """,
        (
            session["user_id"],
        )
    )

    user = cursor.fetchone()

    conn.close()

    if not user:

        session.clear()

        return redirect(
            url_for("login")
        )

    return render_template(
        "profile.html",
        user=user
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return {
        "status": "ok",
        "application": "PaddyGuard AI"
    }


# ============================================================
# ERROR - FILE TOO LARGE
# ============================================================

@app.errorhandler(413)
def file_too_large(error):

    if "user_id" in session:

        return render_template(
            "upload.html",
            error=(
                "File is too large. "
                "Maximum allowed size is 10 MB."
            )
        )

    return redirect(
        url_for("login")
    )


# ============================================================
# ERROR - PAGE NOT FOUND
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <h1>Page Not Found</h1>
    <p>The requested PaddyGuard AI page does not exist.</p>
    <a href="/">Go to Home</a>
    """, 404


# ============================================================
# ERROR - INTERNAL SERVER ERROR
# ============================================================

@app.errorhandler(500)
def internal_server_error(error):

    print(
        "Internal server error:",
        error
    )

    return """
    <h1>PaddyGuard AI - Server Error</h1>
    <p>Something went wrong on the server.</p>
    <a href="/">Go to Home</a>
    """, 500


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "PaddyGuard AI - Flask Application"
    )

    print("=" * 60)

    print(
        "Database:",
        DATABASE
    )

    print(
        "Upload folder:",
        UPLOAD_FOLDER
    )

    print(
        "Model classes:",
        load_classes()
    )

    print("=" * 60)

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )