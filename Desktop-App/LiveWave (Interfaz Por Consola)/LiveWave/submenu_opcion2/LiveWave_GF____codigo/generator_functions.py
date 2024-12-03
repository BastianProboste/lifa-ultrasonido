import time  # Importación estándar para delays en la ejecución del genrador
import dg1022  # Importación de Manejo de generador de funciones
def set_gaussian_wave(frequency, cycles, amplitude_low):
    """
    Establece la frecuencia y amplitud en el generador de funciones Rigol DG1022.

    Parameters:
    frequency (float): Frecuencia de salida en Hz
    cycles (int): Voltaje máximo (HIGH) en V
    amplitude_low (float): Voltaje mínimo (LOW) en V
    """
    generator = dg1022.dg1022()
    generator.conect(0)  # Conectar al puerto 0
    time.sleep(0.5)  # Esperar a que la conexión se realice correctamente

    # Configuración del generador
    generator.gauss(float(frequency) * 1e6, float(cycles), float(amplitude_low))
    generator.write("FUNC USER")
    generator.write("TRIGger:SOURce IMM")
    generator.write("BURS:MODE TRIG")
    generator.use_custom_signal()
    generator.write("BURS:STAT ON")
    generator.write("BURS:INT:PER 0.01")
    generator.write("BURS:NCYC 1")
    generator.write("APPLy:SINusoid:CH2 4800,1.0,0.0")
    generator.write("OUTP:CH2 ON")

def get_burst_state():
    """
    Consulta y devuelve el estado del modo ráfaga (BURSt:STATe?) del generador Rigol DG1022.
    """
    results=[]
    generator = dg1022.dg1022()
    generator.conect(0)  # Conectar al puerto 0
    time.sleep(0.5)
    generator.write("BURSt:MODE?")
    Encendido= (generator.read())
    generator.write("BURSt:STATe?")
    Estado_burst= (generator.read())
    generator.write("BURSt:NCYCles?")
    ciclos=(generator.read())
    print(f"Generador {Encendido}Burst {Estado_burst} ciclos {ciclos}")

def get_channel_state():
    """
    Obtiene y muestra el estado del canal 1 del generador.
    """
    generator = dg1022.dg1022()
    generator.conect(0)  # Conectar al puerto 0
    time.sleep(0.5)
    generator.write("BURSt:MODE?")
    print(generator.read())
    generator.write("BURSt:STATe?")
    print(generator.read())
    generator.write("BURSt:NCYCles?")
    print(generator.read())


def control_burst_mode(enable_burst, num_cycles):
    """
    Controla el modo burst del generador de funciones.

    Parameters:
    enable_burst (bool): Activar (True) o desactivar (False) el modo burst.
    num_cycles (int): Número de ciclos a configurar en el modo burst (solo si está activado).
    """
    generator = dg1022.dg1022()
    generator.conect(0)  # Conectar al puerto 0
    try:
        if enable_burst:
            # Activar modo burst
            generator.write("BURS:STAT ON")
            print("Modo burst activado.")
            generator.write(f"BURS:NCYC {num_cycles}")
            print(f"Número de ciclos configurado: {num_cycles}")
        else:
            # Desactivar modo burst
            generator.write("BURS:STAT OFF")
            print("Modo burst desactivado.")

        time.sleep(0.5)  # Espera para asegurar que los comandos se envían correctamente

    except (IOError, ValueError) as e:
        print(f"Error: {e}")


def configure_sine_wave_signal():
    """
    Configura una señal sinusoidal en el generador de funciones.
    """
    generator = dg1022.dg1022()
    generator.conect(0)  # Conectar al puerto 0
    try:
        # Ingreso de frecuencia (solo valores entre 1 Hz y 5 MHz)
        while True:
            frecuencia_input = input("Ingrese la frecuencia en MHz (1 - 5): ")
            if frecuencia_input.isdigit() and 1 <= int(frecuencia_input) <= 5:
                frecuencia = int(frecuencia_input) * 1e6  # Convertir a Hz
                break
            print("Error: Ingrese un valor entre 1 y 5 MHz.")

        # Ingreso de amplitud (solo valores entre 1 y 3 Vpp)
        while True:
            amplitud_input = input("Ingrese la amplitud en Vpp (1 - 3): ")
            if amplitud_input.isdigit() and 1 <= int(amplitud_input) <= 3:
                amplitud = int(amplitud_input)
                break
            print("Error: Ingrese un valor entre 1 y 3 Vpp.")

        # Ingreso de offset (validar como número flotante o entero)
        while True:
            offset_input = input("Ingrese el valor de offset en voltios (por ejemplo, 0.0): ")
            try:
                offset = float(offset_input)
                break
            except (IOError, ValueError) as e:
                print(f"Error : {e}")
                print("Error: Ingrese un número válido para el offset.")

        # Configuración de la señal en el generador
        generator.write(f"APPLy:SINusoid {frecuencia},{amplitud},{offset}")
        print(
    f"Se ha configurado una señal sinusoidal con {frecuencia / 1e6} MHz, "
    f"{amplitud} Vpp, y {offset} V de offset."
)

    except (IOError, ValueError) as e:
        print(f"Error al configurar la señal: {e}")


def get_channel_configuration():
    """
    Obtiene la configuración del canal seleccionado en el generador.
    """
    generator = dg1022.dg1022()
    generator.conect(0)  # Conectar al puerto 0
    try:
        # Ingreso del canal (validar como número entero)
        while True:
            canal_input = input("Ingrese el canal (1 o 2): ")
            if canal_input.isdigit() and int(canal_input) in [1, 2]:
                canal = int(canal_input)
                break
            print("Error: Ingrese un canal válido (1 o 2).")

        # Obtener la configuración del canal
        generator.write(f"INSTrument:SELect CHANnel{canal}")
        generator.write("APPLy?")
        print(generator.read())

    except (IOError, ValueError) as e:
        print(f"Error al obtener la configuración del canal: {e}")