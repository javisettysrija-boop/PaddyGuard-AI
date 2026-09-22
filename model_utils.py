import os
import numpy as np
from PIL import Image

MODEL = None
CLASS_NAMES = None

MODEL_PATH = os.path.join("model", "paddy_disease_model.keras")
CLASS_PATH = os.path.join("model", "classes.txt")


def load_model_and_classes():
    global MODEL, CLASS_NAMES

    if MODEL is None:
        from tensorflow import keras
        MODEL = keras.models.load_model(MODEL_PATH)

    if CLASS_NAMES is None:
        with open(CLASS_PATH, encoding="utf-8") as f:
            CLASS_NAMES = [line.strip() for line in f if line.strip()]

    return MODEL, CLASS_NAMES


def predict_image(path):
    model, class_names = load_model_and_classes()

    # Open image
    image = Image.open(path).convert("RGB")

    # Resize to the model input size
    image = image.resize((224, 224))

    # Convert image to NumPy array
    # Do NOT normalize here because the trained model
    # already contains its own preprocessing layers.
    array = np.asarray(image, dtype=np.float32)

    # Add batch dimension
    array = np.expand_dims(array, axis=0)

    # Predict
    probabilities = model.predict(array, verbose=0)[0]

    # Get highest probability class
    index = int(np.argmax(probabilities))

    disease = class_names[index]
    confidence = float(probabilities[index] * 100)

    return disease, confidence