from traccion import main
def mostrar_menu_principal():
    print("\n--- MENÚ PRINCIPAL ---")
    print("1. Opción 1: Adquirir Datos")
    print("3. Salir")

def obtener_opcion_valida():
    while True:
        try:
            opcion = int(input("Seleccione una opción (1-3): "))
            if 1 <= opcion <= 3:
                return opcion
            else:
                print("Error: Debe elegir un número entre 1 y 3.")
        except ValueError:
            print("Error: Entrada no válida. Por favor ingrese un número.")

def ejecutar_opcion(opcion):
    if opcion == 2:
        print("hola")  # Llama al submenú y espera que termine
    elif opcion == 3:
        print("Saliendo del programa...")
    else:
        print(f"Opción {opcion} seleccionada (en desarrollo).")

# Programa principal
def mostrar_menu_principal_maquina_traccion():
    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Iniciar toma de datos maquina tracción")
        print("2. Salir")

        try:
            opcion = int(input("Seleccione una opción: "))
            if opcion == 1:
                main()
            elif opcion == 2:
                print("Saliendo del menú...")
                break
            else:
                print("Opción no válida. Por favor, intente de nuevo.")
        except ValueError:
            print("Error: Por favor, ingrese un número.")