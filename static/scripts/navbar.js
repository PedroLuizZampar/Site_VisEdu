document.addEventListener("DOMContentLoaded", function() {
    const toggleButton = document.querySelector('.menu-toggle');
    const navBar = document.querySelector('.NavBar');
    const optionsToggle = document.querySelector('.options-toggle');
    const optionsContainer = document.querySelector('.options-container');

    // Toggle da Navbar
    toggleButton.addEventListener('click', function() {
        navBar.classList.toggle('active');
    });

    // Fecha o menu da navbar ao clicar fora dele
    document.addEventListener('click', function(event) {
        if (!navBar.contains(event.target) && !toggleButton.contains(event.target)) {
            navBar.classList.remove('active');
        }
    });

    // Toggle do menu de opções ao clicar em "Opções"
    optionsToggle.addEventListener('click', function(event) {
        event.preventDefault(); // Impede o comportamento padrão do link
        optionsContainer.classList.toggle('active');
    });

    // Fecha o menu de opções ao clicar fora dele
    document.addEventListener('click', function(event) {
        if (!optionsContainer.contains(event.target) && !optionsToggle.contains(event.target)) {
            optionsContainer.classList.remove('active');
        }
    });
});
