from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_from_directory
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import os
import torch
import torch.nn.functional as F

from PIL import Image
from torchvision import models, transforms

from database.database import (
    get_connection,
    initialize_database
)


# ============================================================
# APPLICATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static"
)

app.secret_key = "lung-cancer-cnn-development-key"


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "best_lung_cancer_resnet18.pth"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ============================================================
# DEVICE
# ============================================================

device = torch.device("cpu")


# ============================================================
# CLASS NAMES
# ============================================================

CLASS_NAMES = [
    "Bengin cases",
    "Malignant cases",
    "Normal cases"
]


# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 60)
print("LOADING LUNG CANCER RESNET18 MODEL")
print("=" * 60)

print("Model path:")
print(MODEL_PATH)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model file not found:\n{MODEL_PATH}"
    )

model = models.resnet18(weights=None)

model.fc = torch.nn.Linear(
    model.fc.in_features,
    len(CLASS_NAMES)
)

checkpoint = torch.load(
    MODEL_PATH,
    map_location=device
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.to(device)
model.eval()

print("Checkpoint loaded successfully.")
print("Saved class names:", checkpoint.get("class_names"))
print("Best epoch:", checkpoint.get("best_epoch"))
print("Best validation loss:", checkpoint.get("best_val_loss"))
print("MODEL LOADED SUCCESSFULLY")


# ============================================================
# IMAGE TRANSFORMATION
# ============================================================

prediction_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_image(image_path):

    image = Image.open(
        image_path
    ).convert("RGB")

    image_tensor = prediction_transform(image)

    image_tensor = image_tensor.unsqueeze(0)

    image_tensor = image_tensor.to(device)

    with torch.no_grad():

        outputs = model(image_tensor)

        probabilities = F.softmax(
            outputs,
            dim=1
        )[0]

    predicted_index = torch.argmax(
        probabilities
    ).item()

    prediction = CLASS_NAMES[predicted_index]

    confidence = (
        probabilities[predicted_index].item()
        * 100
    )

    return {
        "prediction": prediction,
        "confidence": confidence,
        "benign": probabilities[0].item() * 100,
        "malignant": probabilities[1].item() * 100,
        "normal": probabilities[2].item() * 100
    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return render_template("index.html")


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()

        email = request.form["email"].strip()

        password = request.form["password"]

        confirm_password = request.form["confirm_password"]

        if not username or not email or not password:

            flash(
                "Please fill in all fields.",
                "error"
            )

            return redirect(url_for("register"))

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        connection = get_connection()

        try:

            connection.execute(
                """
                INSERT INTO users
                (username, email, password)
                VALUES (?, ?, ?)
                """,
                (
                    username,
                    email,
                    hashed_password
                )
            )

            connection.commit()

            flash(
                "Registration successful. Please login.",
                "success"
            )

            return redirect(url_for("login"))

        except Exception:

            flash(
                "Username or email already exists.",
                "error"
            )

        finally:

            connection.close()

    return render_template("register.html")


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()

        password = request.form["password"]

        connection = get_connection()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]

            session["username"] = user["username"]

            return redirect(url_for("dashboard"))

        flash(
            "Invalid username or password.",
            "error"
        )

    return render_template("login.html")


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

    if "user_id" not in session:

        return redirect(url_for("login"))

    connection = get_connection()

    total = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM predictions
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()["count"]

    benign = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM predictions
        WHERE user_id = ?
        AND prediction = 'Bengin cases'
        """,
        (session["user_id"],)
    ).fetchone()["count"]

    malignant = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM predictions
        WHERE user_id = ?
        AND prediction = 'Malignant cases'
        """,
        (session["user_id"],)
    ).fetchone()["count"]

    normal = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM predictions
        WHERE user_id = ?
        AND prediction = 'Normal cases'
        """,
        (session["user_id"],)
    ).fetchone()["count"]

    connection.close()

    return render_template(
        "dashboard.html",
        username=session["username"],
        total=total,
        benign=benign,
        malignant=malignant,
        normal=normal
    )


# ============================================================
# PREDICT
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    if "user_id" not in session:

        return redirect(url_for("login"))

    if "image" not in request.files:

        flash(
            "Please select an image.",
            "error"
        )

        return redirect(url_for("dashboard"))

    image = request.files["image"]

    if image.filename == "":

        flash(
            "Please select an image.",
            "error"
        )

        return redirect(url_for("dashboard"))

    allowed_extensions = {
        "png",
        "jpg",
        "jpeg",
        "bmp"
    }

    extension = (
        image.filename
        .rsplit(".", 1)[-1]
        .lower()
    )

    if extension not in allowed_extensions:

        flash(
            "Please upload a valid image.",
            "error"
        )

        return redirect(url_for("dashboard"))

    safe_filename = os.path.basename(
        image.filename
    )

    filename = (
        f"{session['user_id']}_{safe_filename}"
    )

    image_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    image.save(image_path)

    result = predict_image(image_path)

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO predictions
        (
            user_id,
            image_filename,
            prediction,
            confidence,
            benign_probability,
            malignant_probability,
            normal_probability
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            filename,
            result["prediction"],
            result["confidence"],
            result["benign"],
            result["malignant"],
            result["normal"]
        )
    )

    connection.commit()

    connection.close()

    return render_template(
        "prediction.html",
        result=result,
        image_filename=filename
    )

# ============================================================
# MODEL PERFORMANCE
# ============================================================

@app.route("/performance")
def performance():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "performance.html"
    )
    
# ============================================================
# HISTORY
# ============================================================

@app.route("/history")
def history():

    if "user_id" not in session:

        return redirect(url_for("login"))

    connection = get_connection()

    predictions = connection.execute(
        """
        SELECT *
        FROM predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "history.html",
        predictions=predictions
    )


# ============================================================
# UPLOADED IMAGES
# ============================================================

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    if "user_id" not in session:

        return redirect(url_for("login"))

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# ============================================================
# CSS/STATIC DEBUG
# ============================================================

@app.route("/debug-static")
def debug_static():

    css_path = os.path.join(
        BASE_DIR,
        "static",
        "style.css"
    )

    js_path = os.path.join(
        BASE_DIR,
        "static",
        "dashboard.js"
    )

    return {
        "base_directory": BASE_DIR,
        "css_exists": os.path.exists(css_path),
        "js_exists": os.path.exists(js_path),
        "css_path": css_path,
        "js_path": js_path
    }


# ============================================================
# DATABASE
# ============================================================

initialize_database()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("LUNGCARE AI")
    print("=" * 60)

    print("Dashboard:")
    print("http://127.0.0.1:5000")

    print("Static folder:")
    print(app.static_folder)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )