let file = document.getElementById("imageInput");
let preview_img = document.getElementById("previewImage");
let message = document.getElementById("message");
let left_move = document.getElementById("left_move")

async function cropAndSaveImage(imageUrl, cropX, cropY, cropWidth, cropHeight, saveFileName) {
    // Create an image element
    const img = new Image();
    
    // Set crossOrigin to anonymous to avoid CORS issues
    img.crossOrigin = "Anonymous";
    
    // Set the src attribute to load the image
    img.src = imageUrl;

    // Wait for the image to load
    await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
    });

    // Create a canvas element
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Set canvas dimensions to cropped area
    canvas.width = cropWidth;
    canvas.height = cropHeight;

    // Draw the cropped image onto the canvas
    ctx.drawImage(img, cropX, cropY, cropWidth, cropHeight, 0, 0, cropWidth, cropHeight);

    // Convert the canvas content to a data URL
    const croppedImageDataUrl = canvas.toDataURL('image/png');


    // Create an anchor element to trigger download
    //const link = document.createElement('a');
    //link.download = saveFileName || 'cropped_image.png';
    //link.href = croppedImageDataUrl;
    //link.click();

}



file.addEventListener("change", () => {
    if (file.files.length){
        preview_img.style.display='block';
        preview_img.src = URL.createObjectURL(file.files[0]);

        cropAndSaveImage(preview_img.src, 0, 0, 224, 224, 'upload.jpg');

        let fileName = file.files[0].name;
        console.log(fileName);
        message.innerHTML = `${fileName}`;
    }

});
