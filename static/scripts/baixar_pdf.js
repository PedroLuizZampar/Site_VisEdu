document.getElementById("baixar").addEventListener("click", () => {
    const elemento = document.querySelector(".content");
    const opcoes = {
        margin:       1,
        filename:     'meu-documento.pdf',
        image:        { type: 'png', quality: 1 },
        html2canvas:  { scale: 2 },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    html2pdf().set(opcoes).from(elemento).save();
});