const backgroundImageInput = document.getElementById("background_image")
const preview = document.getElementById('imagePreview');
// Add a listener to the file input
backgroundImageInput.addEventListener('change', function(event) {
    // Take the uploaded img sent into this file input
    const file = event.target.files[0]; 
    if (file) {
        const reader = new FileReader(); 
        //wait the file/img load into the reader
        reader.onload = function(e) {
            // Set the new file as image src 
            preview.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});