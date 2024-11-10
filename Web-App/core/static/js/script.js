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
/*
$(document).ready(function() {
            // Filtro por texto
            $("#buscador").on("keyup", function() {
                var value = $(this).val().toLowerCase();
                $(".table-row").filter(function() {
                    $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
                });
            });

            // Filtro por rol
            $("#rolBuscador").on("change", function() {
                var rolValue = $(this).val(); // Obtener el valor seleccionado
                $(".table-row").filter(function() {
                    var rowText = $(this).children("td").eq(5).text().trim(); // Asumiendo que el rol está en la sexta columna
                    if (rolValue === "") {
                        $(this).show(); // Mostrar todas las filas si no hay selección
                    } else {
                        $(this).toggle(rowText === rolValue); // Comparar con el valor del selector
                    }
                });
            });
        });

*/
function showUserDetails(userId) {
    $.ajax({
        url: `/module/user_detail/${userId}`,
        type: 'GET',
        success: function(data) {
            // Datos en modal
            document.getElementById("modalUserName").textContent = data.username;
            document.getElementById("modalFirstName").textContent = data.first_name;
            document.getElementById("modalLastName").textContent = data.last_name;
            document.getElementById("modalEmail").textContent = data.email;
            document.getElementById("modalRut").textContent = data.rut;
            document.getElementById("modalRol").textContent = data.rol;
            document.getElementById("modalPhone").textContent = data.phone;

            // Mostrar el campo de carrera solo al ser staff (Docente)
            var carreraField = document.getElementById("modalCarrera");
            var carreraValue = document.getElementById("modalCarreraValue");
            if (data.rol === "Estudiante") {
                carreraField.style.display = 'block'; 
                carreraValue.textContent = data.carrera;
            } else {
                carreraField.style.display = 'none'; // Ocultar carrera si es Docente
            }

            // Mostrar el modal
            document.getElementById("userDetailsModal").style.display = "flex";
        },

        // Alerta por si existe error
        error: function() {
            alert("Error al cargar los datos del usuario.");
        }
    });
}


// Cierra el modal
function closeModal() {
    document.getElementById("userDetailsModal").style.display = "none";
}

// Cierra el modal al hacer clic fuera de él
window.onclick = function(event) {
    const modal = document.getElementById("userDetailsModal");
    if (event.target == modal) {
        modal.style.display = "none";
    }
};


