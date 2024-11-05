document.addEventListener("DOMContentLoaded", function() {
    // Obtenha os botões
    const salasButton = document.getElementById('salas-button');
    const turmasButton = document.getElementById('turmas-button');
    const disciplinaButton = document.getElementById('disciplina-button');
    const periodosButton = document.getElementById('periodos-button');
    const aulasButton = document.getElementById('aulas-button');
    const professoresButton = document.getElementById('professores-button');

    // Função para ativar o botão clicado e desativar o outro
    function activateButton(activeButton) {
        // Remova a classe active de ambos os botões
        salasButton.classList.remove('active');
        turmasButton.classList.remove('active');
        disciplinaButton.classList.remove('active');
        periodosButton.classList.remove('active');
        aulasButton.classList.remove('active');
        professoresButton.classList.remove('active');

        // Adicione a classe active ao botão clicado
        activeButton.classList.add('active');
    }

    // Adicione eventos de clique aos botões
    salasButton.addEventListener('click', () => activateButton(salasButton));
    turmasButton.addEventListener('click', () => activateButton(turmasButton));
    disciplinaButton.addEventListener('click', () => activateButton(disciplinaButton));
    periodosButton.addEventListener('click', () => activateButton(periodosButton));
    aulasButton.addEventListener('click', () => activateButton(aulasButton));
    professoresButton.addEventListener('click', () => activateButton(professoresButton));
});