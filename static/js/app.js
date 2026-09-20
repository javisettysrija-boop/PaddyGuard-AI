document.addEventListener("DOMContentLoaded", function () {

    console.log("PaddyGuard AI frontend loaded successfully.");


    // Image preview

    const imageInput = document.getElementById("image");

    const imagePreview = document.getElementById("imagePreview");


    if (imageInput && imagePreview) {

        imageInput.addEventListener("change", function () {

            const file = this.files[0];

            if (file) {

                const reader = new FileReader();

                reader.onload = function (event) {

                    imagePreview.src = event.target.result;

                    imagePreview.classList.remove("d-none");

                };

                reader.readAsDataURL(file);
            }

        });
    }


    // Upload form validation

    const uploadForm = document.getElementById("uploadForm");


    if (uploadForm) {

        uploadForm.addEventListener("submit", function () {

            const button =
                uploadForm.querySelector("button[type='submit']");

            if (button) {

                button.disabled = true;

                button.innerHTML =
                    "Analyzing Paddy Leaf...";

            }

        });

    }

});