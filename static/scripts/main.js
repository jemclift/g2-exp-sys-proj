function previewFile(element) {

    const reader = new FileReader();
    reader.readAsDataURL(element.files[0]);

    reader.addEventListener("load", function () {

        document.getElementById("img-base64-txt").value = reader.result

    }, false);

}