function confirmDelete() {
    Swal.fire({
        title: "¿Estás seguro?",
        text: "Este usuario sera eliminado",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Si"
      }).then((result) => {
        if (result.isConfirmed) {
          Swal.fire({
            text: "Usuario Eliminado",
            icon: "success"
          });
        }
      });
}

function mostrarDetallesUsuario(userId) {
    $.ajax({
        url: `/module/detalles_usuario/${userId}/`,  // Asumimos que este es el URL correcto para la vista 'detalles_usuario'
        type: 'GET',
        success: function(datos) {
            // Llenar los datos en el modal
            document.getElementById("modalUserName").textContent = datos.username;
            document.getElementById("modalFirstName").textContent = datos.first_name;
            document.getElementById("modalLastName").textContent = datos.last_name;
            document.getElementById("modalEmail").textContent = datos.email;
            document.getElementById("modalRut").textContent = datos.rut;
            document.getElementById("modalRol").textContent = datos.rol;
            document.getElementById("modalTelefono").textContent = datos.telefono;

            // Mostrar el campo de carrera solo si el usuario es un estudiante
            var carreraField = document.getElementById("modalCarrera");
            var carreraValue = document.getElementById("modalCarreraValue");
            if (datos.rol === "Estudiante") {
                carreraField.style.display = 'block';
                carreraValue.textContent = datos.carrera;
            } else {
                carreraField.style.display = 'none'; // Ocultar carrera si es Docente
            }

            // Mostrar el modal
            document.getElementById("detallesUsuarioModal").style.display = "flex";
        },
        error: function() {
            alert("Error al cargar los datos del usuario.");
        }
    });
}

function cerrar_Modal() {
    document.getElementById("detallesUsuarioModal").style.display = "none";
}

// Cerrar el modal al hacer clic fuera de él
window.onclick = function(event) {
    const modal = document.getElementById("detallesUsuarioModal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
};
