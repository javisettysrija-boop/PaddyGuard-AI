import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
import matplotlib.pyplot as plt


IMG_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42

TEST_DIR = "dataset/test"
MODEL_PATH = "model/paddy_disease_model.keras"
MODEL_DIR = "model"


# Load trained model
model = keras.models.load_model(MODEL_PATH)


# Load test dataset
test_ds = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    seed=SEED,
    label_mode="categorical",
    shuffle=False
)

class_names = test_ds.class_names

print("Test classes:", class_names)
print("Number of classes:", len(class_names))


# Get predictions
y_true = []
y_pred = []

for images, labels in test_ds:

    predictions = model.predict(images, verbose=0)

    predicted_classes = np.argmax(predictions, axis=1)
    true_classes = np.argmax(labels.numpy(), axis=1)

    y_pred.extend(predicted_classes)
    y_true.extend(true_classes)


# Accuracy
accuracy = accuracy_score(y_true, y_pred)

print("\nTest Accuracy:", accuracy)


# Precision
precision = precision_score(
    y_true,
    y_pred,
    average="weighted",
    zero_division=0
)

# Recall
recall = recall_score(
    y_true,
    y_pred,
    average="weighted",
    zero_division=0
)

# F1 Score
f1 = f1_score(
    y_true,
    y_pred,
    average="weighted",
    zero_division=0
)


print("Weighted Precision:", precision)
print("Weighted Recall:", recall)
print("Weighted F1 Score:", f1)


# Classification report
print("\nClassification Report:")
print(
    classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        zero_division=0
    )
)


# Confusion matrix
cm = confusion_matrix(y_true, y_pred)


plt.figure(figsize=(10, 8))

plt.imshow(cm)

plt.title("Paddy Disease Classification - Confusion Matrix")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")

plt.xticks(
    range(len(class_names)),
    class_names,
    rotation=45,
    ha="right"
)

plt.yticks(
    range(len(class_names)),
    class_names
)

plt.colorbar()

for i in range(len(class_names)):
    for j in range(len(class_names)):
        plt.text(
            j,
            i,
            cm[i, j],
            ha="center",
            va="center"
        )

plt.tight_layout()

plt.savefig(
    os.path.join(MODEL_DIR, "confusion_matrix.png")
)

plt.show()

print("\nConfusion matrix saved:")
print("model/confusion_matrix.png")

print("\nEvaluation completed.")