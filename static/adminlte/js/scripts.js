// Capturar datos del cliente y abrir el modal para edición
function openEditForm() {
    const detailsContainer = document.getElementById("detalles");
    
    if (!detailsContainer) {
        console.error("No se encontró el contenedor con ID 'detalles'.");
        return;
    }

    const dataElements = detailsContainer.querySelectorAll("strong");

    if (dataElements.length < 5) {
        console.error("No se encontraron suficientes elementos de datos en #detalles.");
        return;
    }

    // Extraer datos de los elementos
    const nombre = dataElements[0].textContent.split(": ")[1];
    const rut = dataElements[1].textContent.split(": ")[1];
    const correo = dataElements[2].textContent.split(": ")[1];
    const telefono = dataElements[3].textContent.split(": ")[1];
    const direccion = dataElements[4].textContent.split(": ")[1];

    // Asignar los valores extraídos a los campos del formulario del modal
    document.getElementById("name").value = nombre || "";
    document.getElementById("rut").value = rut || "";
    document.getElementById("email").value = correo || "";
    document.getElementById("phone").value = telefono || "";
    document.getElementById("address").value = direccion || "";

    // Mostrar el modal
    const modal = new bootstrap.Modal(document.getElementById("editClientModal"));
    modal.show();
}

// Enviar datos actualizados al servidor
async function saveClientData() {
    const name = document.getElementById("name").value;
    const rut = document.getElementById("rut").value;
    const email = document.getElementById("email").value;
    const phone = document.getElementById("phone").value;
    const address = document.getElementById("address").value;

    const data = {
        name,
        rut,
        email,
        phone,
        address
    };

    console.log("Datos enviados:", data);

    try {
        const response = await fetch("/update-client-url", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`Error en la solicitud: ${response.statusText}`);
        }

        const result = await response.json();
        console.log("Respuesta del servidor:", result);

        // Cerrar el modal y actualizar los datos en la página si es necesario
        const modal = bootstrap.Modal.getInstance(document.getElementById("editClientModal"));
        modal.hide();

        // Aquí puedes actualizar el contenido de #detalles con los nuevos datos
        // Ejemplo:
        document.getElementById("detalles").innerHTML = `
            <strong>Nombre: ${data.name}</strong><br>
            <strong>RUT: ${data.rut}</strong><br>
            <strong>Correo Electrónico: ${data.email}</strong><br>
            <strong>Teléfono: ${data.phone}</strong><br>
            <strong>Dirección: ${data.address}</strong>
        `;
    } catch (error) {
        console.error("Error al guardar los datos del cliente:", error);
        alert("Ocurrió un error al guardar los datos. Por favor, inténtelo nuevamente.");
    }
}