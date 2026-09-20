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

    image = Image.open(path).convert("RGB")
    image = image.resize((224, 224))

    array = np.asarray(image, dtype=np.float32)
    array = np.expand_dims(array, axis=0)
    array = (array / 127.5) - 1.0

    probabilities = model.predict(array, verbose=0)[0]

    index = int(np.argmax(probabilities))
    disease = class_names[index]
    confidence = float(probabilities[index] * 100)

    return disease, confidence