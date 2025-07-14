document.addEventListener('DOMContentLoaded', function() {
    const planesSelect = document.getElementById('id_planes');
    const totalDisplay = document.getElementById('total-display');

    function updateTotal() {
        let total = 0;
        const selectedOptions = Array.from(planesSelect.selectedOptions);
        selectedOptions.forEach(option => {
            total += parseFloat(option.dataset.precio || 0);
        });
        totalDisplay.textContent = `Total: $${total.toFixed(2)}`;
    }

    planesSelect.addEventListener('change', updateTotal);
    updateTotal(); // Inicializar
});
