let modal = document.getElementById("modal");

let newUpload = document.getElementById("enviar-upload");
let editUpload = document.getElementById("edit-upload");

newUpload.onclick = function() {
    // Limpa os campos do formulário
    let inputs = modal.querySelectorAll('input');
    inputs.forEach(input => input.value = '');

    modal.showModal();
}
