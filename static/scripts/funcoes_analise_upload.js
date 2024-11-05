function iniciarAnaliseTodos() {
    document.getElementById('mensagem_analise').showModal();
    localStorage.setItem('modal_analise_aberto', 'true');

    fetch(`/upload/analise_todos`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log('Análise iniciada:', data);
    })
    .catch(error => {
        console.error('Erro ao iniciar a análise:', error);
    });
}

document.addEventListener("DOMContentLoaded", function() {
    if (localStorage.getItem('modal_analise_aberto') === 'true') {
        const modalAnalise = document.getElementById('mensagem_analise');
        modalAnalise.showModal();

        const statusInterval = setInterval(async () => {
            try {
                const response = await fetch(`/upload/progress`);
                const data = await response.json();

                // Atualiza o texto do progresso e a largura da barra
                document.getElementById('progress-text').innerText = `Progresso: ${data.progress.toFixed(0)}%`;
                document.getElementById('progress-bar').style.width = `${data.progress}%`;

                // Verifica se o progresso atingiu 100% ou se o status é 'concluido'
                if (data.progress >= 100 || data.progress == 0 || data.status === 'concluido') {
                    clearInterval(statusInterval);  // Encerra o intervalo
                    modalAnalise.close();  // Fecha o modal
                    localStorage.removeItem('modal_analise_aberto');
                    location.reload();
                } else if (data.status === 'cancelado') {
                    clearInterval(statusInterval);
                    modalAnalise.close();
                    localStorage.removeItem('modal_analise_aberto');
                    location.reload();
                }
            } catch (error) {
                console.error('Erro ao verificar o status da análise:', error);
                clearInterval(statusInterval); // Para o intervalo em caso de erro
                modalAnalise.close(); // Fecha o modal em caso de erro
            }
        }, 1000);
    }

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            event.preventDefault(); // Impede o fechamento com a tecla Escape
        }
    });
});