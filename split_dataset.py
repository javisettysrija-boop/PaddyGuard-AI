import os
import random
import shutil

SOURCE_DIR = r"C:\Users\hp\Downloads\paddy-disease-classification\train_images"
DEST_DIR = r"C:\Users\hp\PaddyGuard-AI\dataset"

random.seed(42)

classes = [
    "bacterial_leaf_blight",
    "bacterial_leaf_streak",
    "bacterial_panicle_blight",
    "blast",
    "brown_spot",
    "dead_heart",
    "downy_mildew",
    "hispa",
    "normal",
    "tungro"
]

extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif")

for class_name in classes:

    source_class = os.path.join(SOURCE_DIR, class_name)

    if not os.path.exists(source_class):
        print("Missing class:", class_name)
        continue

    images = [
        f for f in os.listdir(source_class)
        if f.lower().endswith(extensions)
    ]

    random.shuffle(images)

    total = len(images)

    train_end = int(total * 0.70)
    validation_end = train_end + int(total * 0.15)

    train_images = images[:train_end]
    validation_images = images[train_end:validation_end]
    test_images = images[validation_end:]

    splits = {
        "train": train_images,
        "validation": validation_images,
        "test": test_images
    }

    print("\n", class_name)
    print("Total:", total)
    print("Train:", len(train_images))
    print("Validation:", len(validation_images))
    print("Test:", len(test_images))

    for split, split_images in splits.items():

        destination_class = os.path.join(
            DEST_DIR,
            split,
            class_name
        )

        os.makedirs(destination_class, exist_ok=True)

        for image in split_images:

            source_file = os.path.join(
                source_class,
                image
            )

            destination_file = os.path.join(
                destination_class,
                image
            )

            shutil.copy2(source_file, destination_file)

print("\nDataset split completed successfully!")