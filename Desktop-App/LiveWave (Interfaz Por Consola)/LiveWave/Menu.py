from colorama import Fore, Back, Style, init
import time
from submenu_opcion3.menu2 import mostrar_menu_principal_tarjeta_ad
from submenu_opcion4.menu2 import mostrar_menu_principal_tiepie
from submenu_opcion2.menu import generador_funciones_menu
from submenu_opcion5.menu2 import mostrar_menu_principal_maquina_traccion
from submenu_opcion6.menu2 import mostrar_menu_principal_camara
from submenu_opcion7.menu2 import mostrar_menu_principal_ejecucion

# Inicializar colorama
init(autoreset=True)

def animar_titulo(titulo):
    """Simula una animación al mostrar el título del menú."""
    for char in titulo:
        print(Fore.BLUE + Style.BRIGHT + char, end="", flush=True)  # Titulo en azul
        time.sleep(0.05)
    print("\n" + Fore.MAGENTA + "-" * 40)  # Línea divisoria morada

def mostrar_menu_principal():
    """Muestra el menú principal con estilos."""
    print("\n")
    animar_titulo("🎉 BIENVENIDO AL MENÚ DE LIVEWAVE ULTRASONIDO LIFA 🎉")
    print( "Seleccione una de las opciones disponibles:\n")  # Texto blanco para las instrucciones
    
    opciones = [
        "1. Tarjeta de Adquisición",
        "2. Generador de Funciones",
        "3. TiePie",
        "4. Máquina de Tracción",
        "5. Cámara",
        "6. Iniciar Ensayo",
        "7. Salir"
    ]
    
    for opcion in opciones:
        print(Fore.WHITE + Style.BRIGHT + f"{opcion}")  # Opciones en blanco
        time.sleep(0.1)  # Pausa para efecto visual
    print(Fore.MAGENTA + "-" * 40)  # Línea divisoria morada

def obtener_opcion_valida():
    """Solicita al usuario una opción válida."""
    while True:
        try:
            opcion = int(input("Seleccione una opción (1-7): "))  # Entrada azul
            if 1 <= opcion <= 7:
                return opcion
            else:
                print(Fore.RED + " Error: Debe elegir un número entre 1 y 7.")  # Error en rojo
        except ValueError:
            print(Fore.RED + " Error: Entrada no válida. Por favor ingrese un número.")  # Error en rojo

def ejecutar_opcion(opcion):
    """Ejecuta la acción correspondiente a la opción seleccionada."""
    if opcion == 1:
        mostrar_menu_principal_tarjeta_ad()                     
    elif opcion == 2:
        generador_funciones_menu()
    elif opcion == 3:
        mostrar_menu_principal_tiepie()
    elif opcion == 4:
        mostrar_menu_principal_maquina_traccion()
    elif opcion == 5:
        mostrar_menu_principal_camara()
    elif opcion == 6:
        mostrar_menu_principal_ejecucion()
    elif opcion == 7:
        print(" Gracias por usar el programa. ¡Hasta pronto!")  # Despedida en morado
        time.sleep(1)

if __name__ == "__main__":
    while True:
        mostrar_menu_principal()
        opcion = obtener_opcion_valida()
        if opcion == 7:
            ejecutar_opcion(opcion)
            break
        else:
            ejecutar_opcion(opcion)
            input( "Presione Enter para regresar al menú principal...")  # Mensaje en azul
