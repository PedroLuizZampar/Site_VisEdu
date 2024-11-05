document.addEventListener("DOMContentLoaded", function() {
    const toggleButton = document.querySelector('.menu-toggle');
    const navBar = document.querySelector('.NavBar');
    
    toggleButton.addEventListener('click', function() {
        navBar.classList.toggle('active'); // Alterna a classe 'active' na navbar para mostrar/esconder o menu
    });
});