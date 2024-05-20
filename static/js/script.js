let file = document.getElementById("imageInput");
let preview_img = document.getElementById("previewImage");
let message = document.getElementById("message");
let left_move = document.getElementById("left_move")




file.addEventListener("change", () => {
    if (file.files.length){
        preview_img.style.display='block';
        preview_img.src = URL.createObjectURL(file.files[0]);

        

        let fileName = file.files[0].name;
        console.log(fileName);
        message.innerHTML = `${fileName}`;
    }

});
