import os

folders = [
    "dataset/train",
    "dataset/validation",
    "dataset/test"
]

extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif")

for folder in folders:
    print("\nChecking:", folder)

    if not os.path.exists(folder):
        print("Folder does not exist!")
        continue

    total = 0

    for class_name in os.listdir(folder):
        class_path = os.path.join(folder, class_name)

        if os.path.isdir(class_path):
            count = 0

            for file in os.listdir(class_path):
                if file.lower().endswith(extensions):
                    count += 1

            print(class_name, ":", count, "images")
            total += count

    print("Total images:", total)