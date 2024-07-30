let modal = document.getElementById("modal");

let addUpload = document.getElementById("enviar-upload");
let editUpload = document.getElementById("edit-upload");

addUpload.onclick = function() {
    // Limpa os campos do formulário
    let inputs = modal.querySelectorAll('input');
    inputs.forEach(input => input.value = '');

    modal.showModal();
}

editUpload.onclick = function() {
    // Limpa os campos do formulário
    let inputs = modal.querySelectorAll('input');
    inputs.forEach(input => input.value = '');

    modal.showModal();
}
