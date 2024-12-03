# traccion.py

import serial
import threading
import time
import os
from datetime import datetime

class SerialReader(threading.Thread):
    """
    Hilo dedicado para leer datos desde el puerto serial y disparar la adquisición.
    """

    def __init__(self, trigger_acquisition_callback, lecturas_folder, callback_ensayo_end=None):
        super().__init__()
        self.puerto = "COM8"  # Cambia esto al puerto correcto
        self.baudrate = 9600  # Cambia esto al baudrate correcto
        self.ser = serial.Serial(port=self.puerto, baudrate=self.baudrate, timeout=0)
        self.buffer = ""
        self.lecturas = []
        self.trigger_acquisition_callback = trigger_acquisition_callback
        self.callback_ensayo_end = callback_ensayo_end
        self.stop_event = threading.Event()
        self.lecturas_folder = lecturas_folder  # Carpeta para guardar las lecturas

    def run(self):
        """
        Método principal del hilo que lee y procesa los datos del puerto serial.
        """
        try:
            while not self.stop_event.is_set():
                respuesta_bytes = self.ser.read(1024)  # Leer hasta 1024 bytes disponibles
                if respuesta_bytes:
                    respuesta_string = respuesta_bytes.decode('utf-8', errors='ignore')
                    self.buffer += respuesta_string

                    while '{' in self.buffer and '}' in self.buffer:
                        inicio = self.buffer.index('{')
                        fin = self.buffer.index('}') + 1
                        lectura_completa = self.buffer[inicio:fin]
                        self.buffer = self.buffer[fin:]

                        datos = lectura_completa.strip('{}').split(',')

                        if len(datos) > 3 and datos[3] == '0.000':
                            if self.lecturas:
                                # Guarda las lecturas en un archivo de texto
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = os.path.join(self.lecturas_folder, f"lecturas_{timestamp}.txt")
                                with open(filename, "w") as archivo:
                                    for lectura in self.lecturas:
                                        archivo.write(f"{lectura}\n")
                                print(f"Archivo guardado: {filename}")
                                self.lecturas = []  # Reinicia las lecturas para la siguiente sesión
                                # Trigger the ensayo end callback
                                if self.callback_ensayo_end:
                                    self.callback_ensayo_end()
                            continue  # No guarda esta lectura y continúa con la siguiente iteración

                        self.lecturas.append(datos)
                        # Dispara la adquisición inmediatamente
                        self.trigger_acquisition_callback(datos)

                else:
                    time.sleep(0.001)  # Pequeña pausa para no saturar la CPU

        except Exception as e:
            print(f"Error en la lectura del puerto serial: {e}")
        finally:
            if self.ser.is_open:
                self.ser.close()
            print("Puerto serial cerrado.")

    def stop(self):
        """
        Detiene el hilo de lectura.
        """
        self.stop_event.set()

def main():
    """
    Función principal para diagnosticar el puerto COM.
    """
    print("Iniciando diagnóstico del puerto COM...")

    def trigger_acquisition_dummy(datos):
        """
        Función de callback que imprime los datos recibidos.
        """
        print(f"Datos recibidos: {datos}")

    lecturas_folder = os.path.join(os.getcwd(), "Test-lecturas")
    os.makedirs(lecturas_folder, exist_ok=True)

    try:
        reader = SerialReader(trigger_acquisition_dummy, lecturas_folder)
        print(f"Conectando al puerto {reader.puerto} con baudrate {reader.baudrate}...")
        reader.start()

        print("Presiona Ctrl+C para detener el diagnóstico.")
        while reader.is_alive():
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nDiagnóstico detenido por el usuario.")
    except serial.SerialException as e:
        print(f"Error al conectar con el puerto serial: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        if 'reader' in locals() and reader.is_alive():
            print("Deteniendo el lector de puerto serial...")
            reader.stop()
            reader.join()
        print("Diagnóstico finalizado.")

if __name__ == "__main__":
    main()
