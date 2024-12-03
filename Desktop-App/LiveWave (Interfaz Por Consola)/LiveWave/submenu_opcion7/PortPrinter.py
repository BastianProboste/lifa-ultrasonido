import serial

# Configuración del puerto COM
puerto = "COM8"  # Cambia esto por el nombre de tu puerto COM
baudrate = 9600  # Velocidad en baudios
timeout = 1      # Tiempo de espera en segundos

try:
    # Abriendo el puerto serial
    with serial.Serial(puerto, baudrate, timeout=timeout) as ser:
        print(f"Conectado al puerto {puerto}")
        print("Leyendo datos (presiona Ctrl+C para detener)...")

        while True:
            # Leer datos del puerto
            linea = ser.readline().decode("utf-8").strip()
            if linea:  # Si hay datos, imprímelos
                print(f"Datos recibidos: {linea}")

except serial.SerialException as e:
    print(f"Error al abrir el puerto {puerto}: {e}")
except KeyboardInterrupt:
    print("\nLectura detenida por el usuario.")
