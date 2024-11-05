function grafico_media_comportamentos(uploadId) {
    fetch(`/upload/${uploadId}/relatorio/media_comportamentos`)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('canvas_grafico').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Média de Alunos por Comportamentos',
                        data: data.data,
                        backgroundColor: [
                            'rgba(75, 192, 192, 0.6)',
                            'rgba(255, 206, 86, 0.6)',
                            'rgba(255, 99, 132, 0.6)',
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(153, 102, 255, 0.6)',
                            'rgba(255, 159, 64, 0.6)'
                        ],
                        borderColor: [
                            'rgba(75, 192, 192, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            ticks: {
                                font: {
                                    size: 14 // Aumenta o tamanho da fonte dos labels do eixo X
                                },
                                callback: function(value, index) {
                                    // Quebra o texto em duas linhas
                                    const label = this.getLabelForValue(value);
                                    const words = label.split(' ');
                                    if (words.length > 1) {
                                        return [words[0], words.slice(1).join(' ')];
                                    } else {
                                        return label;
                                    }
                                }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Quantidade de Alunos',
                                font: {
                                    size: 16,
                                    weight: 'bold'
                                }
                            },
                            ticks: {
                                font: {
                                    size: 14 // Aumenta o tamanho da fonte dos labels do eixo Y
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom',
                            labels: {
                                padding: 30,
                                font: {
                                    size: 14
                                },
                                generateLabels: function(chart) {
                                    const datasets = chart.data.datasets;
                                    if (datasets.length) {
                                        return chart.data.labels.map(function(label, index) {
                                            return {
                                                text: `${label}: ${datasets[0].data[index].toFixed(0)}`,
                                                fillStyle: datasets[0].backgroundColor[index],
                                                strokeStyle: datasets[0].borderColor[index],
                                                lineWidth: datasets[0].borderWidth,
                                                hidden: false,
                                                index: index
                                            };
                                        });
                                    } else {
                                        return [];
                                    }
                                }
                            }
                        }
                    }
                }
            });
        });

    // Adiciona o botão de download após criar o gráfico
    addDownloadButton();
}

function grafico_contagem_alunos_comportamentos(uploadId) {
    fetch(`/upload/${uploadId}/relatorio/contagem_alunos_comportamentos`)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('canvas_grafico').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Contagem de Alunos por Comportamentos',
                        data: data.data,
                        backgroundColor: [
                            'rgba(75, 192, 192, 0.6)',   // Dormindo
                            'rgba(255, 206, 86, 0.6)',   // Prestando Atenção
                            'rgba(255, 99, 132, 0.6)',   // Mexendo no Celular
                            'rgba(54, 162, 235, 0.6)',   // Copiando
                            'rgba(153, 102, 255, 0.6)',  // Disperso
                            'rgba(255, 159, 64, 0.6)'    // Trabalho em Grupo
                        ],
                        borderColor: [
                            'rgba(75, 192, 192, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            ticks: {
                                font: {
                                    size: 14
                                },
                                callback: function(value, index) {
                                    const label = this.getLabelForValue(value);
                                    const words = label.split(' ');
                                    if (words.length > 1) {
                                        return [words[0], words.slice(1).join(' ')];
                                    } else {
                                        return label;
                                    }
                                }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Quantidade de Alunos',
                                font: {
                                    size: 16,
                                    weight: 'bold'
                                }
                            },
                            ticks: {
                                font: {
                                    size: 14
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom',
                            labels: {
                                padding: 30,
                                font: {
                                    size: 14
                                },
                                generateLabels: function(chart) {
                                    const datasets = chart.data.datasets;
                                    if (datasets.length) {
                                        return chart.data.labels.map(function(label, index) {
                                            return {
                                                text: `${label}: ${datasets[0].data[index]}`,
                                                fillStyle: datasets[0].backgroundColor[index],
                                                strokeStyle: datasets[0].borderColor[index],
                                                lineWidth: datasets[0].borderWidth,
                                                hidden: false,
                                                index: index
                                            };
                                        });
                                    } else {
                                        return [];
                                    }
                                }
                            }
                        }
                    }
                }
            });
        });

        // Adiciona o botão de download após criar o gráfico
        addDownloadButton();
}

function fecharModalRelatorio() {
    const downloadButton = document.getElementById('download-pdf-button');
    if (downloadButton) {
        downloadButton.remove(); // Remove o botão de download
    }
    document.getElementById('relatorio').close(); // Fecha o modal
}

function addDownloadButton() {
    const buttonContainer = document.getElementById('botoes-modal-relatorio');
    buttonContainer.style.textAlign = 'center';
    buttonContainer.style.marginTop = '20px';

    const downloadButton = document.createElement('button');
    downloadButton.textContent = 'Baixar PDF';
    downloadButton.onclick = downloadPDF;
    downloadButton.style.padding = '10px 20px';
    downloadButton.style.fontSize = '16px';
    downloadButton.style.cursor = 'pointer';
    downloadButton.id = 'download-pdf-button'

    buttonContainer.appendChild(downloadButton);
    document.getElementById('canvas_grafico').parentNode.insertBefore(buttonContainer, document.getElementById('canvas_grafico').nextSibling);
}

function downloadPDF() {
    const canvas = document.getElementById('canvas_grafico');
    
    html2canvas(canvas).then(canvas => {
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jspdf.jsPDF();
        const imgProps = pdf.getImageProperties(imgData);
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
        
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save('analise_comportamentos.pdf');
    });
}