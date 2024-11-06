function baixarPDF (nomeRelatorio) {

    const dataAtual = new Date();
    
    const dia = dataAtual.getDate();
    const mes = dataAtual.getMonth() + 1;
    const ano = dataAtual.getFullYear();
    
    const horas = dataAtual.getHours();
    const minutos = dataAtual.getMinutes();
    const segundos = dataAtual.getSeconds();

    const elemento = document.querySelector(".content");
    const opcoes = {
        margin:       1,
        filename:     `${nomeRelatorio}-${ano}-${mes}-${dia}-${horas}-${minutos}-${segundos}.pdf`,
        image:        { type: 'png', quality: 1 },
        html2canvas:  { scale: 2 },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    html2pdf().set(opcoes).from(elemento).save();
}