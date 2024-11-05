document.addEventListener("DOMContentLoaded", function() {
    // Obtenha os botões
    const naoAnalisadosButton = document.getElementById('nao_analisados_button');
    const analisadosButton = document.getElementById('analisados_button');
    // Função para ativar o botão clicado e desativar o outro
    function activateButton(activeButton) {
        // Remova a classe active de ambos os botões
        naoAnalisadosButton.classList.remove('active');
        analisadosButton.classList.remove('active');

        // Adicione a classe active ao botão clicado
        activeButton.classList.add('active');
    }

    // Adicione eventos de clique aos botões
    naoAnalisadosButton.addEventListener('click', () => activateButton(naoAnalisadosButton));
    analisadosButton.addEventListener('click', () => activateButton(analisadosButton));
});