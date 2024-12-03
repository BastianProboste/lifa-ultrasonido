# LectorTraccion.py

import serial
import threading
import time
import os
from datetime import datetime
import traceback
import atexit
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LectorSerial(threading.Thread): # antiguito SerialReader
    """
    Hilo dedicado a la lectura de datos desde el puerto serial y al disparo
    de la adquisición cuando se cumplen ciertas condiciones.
    """

    def __init__(
        self,
        callback_disparo_adquisicion, # antiguito trigger_acquisition_callback
        carpeta_lecturas, # antiguito lecturas_folder
        callback_fin_ensayo=None, # antiguito callback_ensayo_end
        puerto="COM8",
        baudrate=9600
    ):
        """
        Inicializa el lector serial.

        Parámetros:
        - callback_disparo_adquisicion: Función a llamar cuando se dispara la adquisición.
        - carpeta_lecturas: Ruta a la carpeta donde se guardarán las lecturas.
        - callback_fin_ensayo: Función a llamar cuando el ensayo ha finalizado.
        - puerto: Nombre del puerto serial.
        - baudrate: Baudrate para la comunicación serial.
        """
        super().__init__()
        self.puerto = puerto
        self.baudrate = baudrate
        self.callback_disparo_adquisicion = callback_disparo_adquisicion
        self.callback_fin_ensayo = callback_fin_ensayo
        self.carpeta_lecturas = carpeta_lecturas
        self.ser = None
        self.buffer = ""
        self.lecturas = []
        self.evento_detener = threading.Event()
        atexit.register(self.cerrar_puerto_serial)

    def run(self):
        """
        Método principal del hilo que lee y procesa los datos del puerto serial.
        """
        try:
            self.ser = serial.Serial(
                port=self.puerto,
                baudrate=self.baudrate,
                timeout=0
            )
            logging.info(f"Conectado al puerto {self.puerto} con baudrate {self.baudrate}.")

            while not self.evento_detener.is_set():
                try:
                    datos_bytes = self.ser.read(1024)
                    if datos_bytes:
                        datos_str = datos_bytes.decode('utf-8', errors='ignore')
                        self.buffer += datos_str

                        while '{' in self.buffer and '}' in self.buffer:
                            inicio = self.buffer.index('{')
                            fin = self.buffer.index('}') + 1
                            lectura_completa = self.buffer[inicio:fin]
                            self.buffer = self.buffer[fin:]

                            datos = lectura_completa.strip('{}').split(',')

                            if len(datos) > 3 and datos[3] == '0.000':
                                if self.lecturas:
                                    self.guardar_lecturas()
                                    self.lecturas = []
                                    if self.callback_fin_ensayo:
                                        self.callback_fin_ensayo()
                                continue

                            self.lecturas.append(datos)
                            # Dispara la adquisición inmediatamente
                            self.callback_disparo_adquisicion(datos)

                    else:
                        time.sleep(0.001)  # Pequeña pausa para no saturar la CPU

                except serial.SerialException as e:
                    logging.error(f"Error en la comunicación serial: {e}")
                    break
                except Exception as e:
                    logging.error(f"Error inesperado en la lectura serial: {e}")
                    traceback.print_exc()
                    break

        except serial.SerialException as e:
            logging.error(f"No se pudo abrir el puerto serial {self.puerto}: {e}")
        except Exception as e:
            logging.error(f"Error inesperado al iniciar el puerto serial: {e}")
            traceback.print_exc()
        finally:
            self.cerrar_puerto_serial()

    def guardar_lecturas(self):
        """
        Guarda las lecturas acumuladas en un archivo de texto.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = os.path.join(
                self.carpeta_lecturas, f"lecturas_{timestamp}.txt"
            )
            with open(nombre_archivo, "w", encoding='utf-8') as archivo:
                for lectura in self.lecturas:
                    archivo.write(f"{','.join(lectura)}\n")
            logging.info(f"Archivo de lecturas guardado: {nombre_archivo}")
        except Exception as e:
            logging.error(f"Error al guardar las lecturas: {e}")
            traceback.print_exc()

    def cerrar_puerto_serial(self):
        """
        Cierra el puerto serial si está abierto.
        """
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                logging.info(f"Puerto serial {self.puerto} cerrado correctamente.")
            except Exception as e:
                logging.error(f"Error al cerrar el puerto serial: {e}")
                traceback.print_exc()

    def detener(self):
        """
        Detiene el hilo de lectura y cierra el puerto serial.
        """
        self.evento_detener.set()
        self.join()
        self.cerrar_puerto_serial()
        logging.info("Lector serial detenido.")

def main():
    """
    Función principal para ejecutar el lector serial de manera independiente.
    Útil para diagnósticos del puerto COM.
    """
    logging.info("Iniciando diagnóstico del puerto COM...")

    def callback_disparo_dummy(datos):
        """
        Función de callback que imprime los datos recibidos.
        """
        logging.info(f"Datos recibidos: {datos}")

    carpeta_lecturas = os.path.join(os.getcwd(), "LecturasDePrueba")
    os.makedirs(carpeta_lecturas, exist_ok=True)

    lector = LectorSerial(
        callback_disparo_dummy,
        carpeta_lecturas,
        puerto="COM8",
        baudrate=9600
    )

    try:
        lector.start()
        logging.info("Presiona Ctrl+C para detener el diagnóstico.")
        while lector.is_alive():
            time.sleep(0.1)

    except KeyboardInterrupt:
        logging.info("Diagnóstico detenido por el usuario.")
    except Exception as e:
        logging.error(f"Error inesperado durante el diagnóstico: {e}")
        traceback.print_exc()
    finally:
        lector.detener()
        logging.info("Diagnóstico finalizado.")

if __name__ == "__main__":
    main()

"""
Cambios de nombres a español
Clases
SerialReader → LectorSerial
Funciones y métodos
__init__ (sin cambio, ya que es estándar en Python)
run → run (sin cambio, ya que es estándar en hilos)
guardar_lecturas (nueva función, no reemplaza nada)
close_serial_port → cerrar_puerto_serial
stop → detener
main → main (sin cambio, ya que es estándar para puntos de entrada en scripts)
Variables
trigger_acquisition_callback → callback_disparo_adquisicion
lecturas_folder → carpeta_lecturas
callback_ensayo_end → callback_fin_ensayo
ser (sin cambio, ya que es descriptivo)
buffer (sin cambio, ya que es descriptivo)
lecturas (sin cambio, ya que es descriptivo)
stop_event → evento_detener
callback_disparo_dummy → callback_disparo_dummy (sin cambio, ya que es estándar para pruebas)
read_bytes → datos_bytes
read_string → datos_str
filename → nombre_archivo
Funciones/métodos añadidos (no existentes en el código original)
guardar_lecturas: Función para guardar lecturas acumuladas en un archivo de texto.
cerrar_puerto_serial: Asegura el cierre del puerto serial incluso en errores o interrupciones.
detener: Detiene el hilo de lectura y cierra el puerto serial de forma ordenada.
Qué se reemplaza del código original
El código original contenía funciones relacionadas con el puerto serial, pero no eran tan explícitas ni organizadas. Aquí está el mapeo de lo que se reemplaza:

La lógica de manejo del puerto en run ahora se organiza más claramente dentro de run, guardar_lecturas, y cerrar_puerto_serial.
El manejo de excepciones en la lectura serial era limitado; ahora tiene robustez con traceback y manejo detallado con logging.
No existía una función explícita como cerrar_puerto_serial; esto se agregó como parte de las mejoras para asegurar robustez y evitar problemas de puertos abiertos.
"""