# -*- coding: utf-8 -*-
"""
Módulo para interactuar con el generador de funciones Rigol DG1022 y un menú de usuario.
"""


from generator_functions import *


def display_menu():
    """
    Muestra el menú de opciones al usuario.
    """
    print("====== MENÚ PRINCIPAL ======")
    print("1. Onda Arbitraria")
    print("2. Ver estado Ciclo Burst y configuración")
    print("3. Configurar señal sinusoidal (frecuencia, amplitud, offset)")
    print("4. Configurar modo Burst y sus ciclos")
    print("5. Ver Canal 1 y Onda Asociada")
    print("6. Encender el generador de funciones")
    print("7. Apagar el generador de funciones")
    print("8. No implementado aún")
    print("9. No implementado aún")
    print("10. Salir")
    print("============================")


def option_1():
    """Maneja la opción 1 del menú para configurar frecuencia y amplitud."""
    while True:
        try:
            frequency = int(input("Ingresa la frecuencia en MHz (1 a 10 MHz): "))
            if frequency < 1 or frequency > 10:
                raise ValueError("La frecuencia debe estar entre 1 y 10 MHz.")
            break
        except ValueError as e:
            print(e)

    while True:
        try:
            cycles = int(input("Ingresa la cantidad de ciclos (1 a 5): "))
            if cycles < 1 or cycles > 5:
                raise ValueError("La cantidad de ciclos debe estar entre 1 y 5.")
            break
        except ValueError as e:
            print(e)

    while True:
        try:
            amplitude = int(input("Ingresa el valor de amplitud (1 a 5): "))
            if amplitude < 1 or amplitude > 5:
                raise ValueError("La amplitud debe estar entre 1 y 5 V.")
            break
        except ValueError as e:
            print(e)

    set_gaussian_wave(frequency, cycles, amplitude)

def option_2():
    """Maneja la opción 2 del menú para consultar el estado de modo ráfaga."""
    get_burst_state()

def option_3():
    """Maneja la opción 3 del menú para configurar la señal sinusoidal."""
    configure_sine_wave_signal()

def option_4():
    """
    Opción 4: Configurar el modo burst del generador de funciones.
    """
    try:
        # Solicitar al usuario si desea activar o desactivar el modo burst
        while True:
            enable_burst_input = input("¿Desea activar el modo burst? (si/no): ").strip().lower()
            if enable_burst_input in ["si", "no"]:
                enable_burst = enable_burst_input == "si"
                break
            print("Por favor, responda con 'si' o 'no'.")

        if enable_burst:
            while True:
                num_cycles = input("Ingrese el número de ciclos para el modo burst: ")
                if num_cycles.isdigit() and int(num_cycles) > 0:
                    control_burst_mode(True, int(num_cycles))
                    break
                print("Error: Ingrese un número de ciclos válido.")
        else:
            control_burst_mode(False, 0)

    except ValueError as e:
        print(f"Error en la configuración del modo burst: {e}")

def option_5():
    """Maneja la opción 5 del menú para ver el estado del canal 1."""
    get_channel_configuration()

def option_6():
    """Maneja la opción 6 del menú para encender el generador de funciones."""
    generator = dg1022.dg1022()
    generator.conect(0)

def option_7():
    """Maneja la opción 7 del menú para apagar el generador de funciones."""
    generator = dg1022.dg1022()
    generator.conect(0)  # Conectar al puerto 0
    time.sleep(0.5)  # Esperar a que la conexión se realice correctamente
    generator.write("OUTP:CH1 ON")
    generator.write("OUTP:CH2 ON")

def option_8():
    """Maneja la opción 8 del menú para seleccionar el canal de salida."""
    print("No implementado aún.")


def option_9():
    """Maneja la opción 9 del menú para consultar el estado de salida."""
    print("No implementado aún.")

def main():
    """Función principal que ejecuta el menú de opciones."""
    while True:
        display_menu()
        try:
            choice = int(input("Selecciona una opción: "))
            if choice == 1:
                option_1()
            elif choice == 2:
                option_2()
            elif choice == 3:
                option_3()
            elif choice == 4:
                option_4()
            elif choice == 5:
                option_5()
            elif choice == 6:
                option_6()
            elif choice == 7:
                option_7()
            elif choice == 8:
                option_8()
            elif choice == 9:
                option_9()
            elif choice == 10:
                print("Saliendo del programa.")
                break
            else:
                print("Opción no válida, intenta de nuevo.")
        except ValueError:
            print("Por favor, ingrese un número válido.")


if __name__ == "__main__":
    main()
