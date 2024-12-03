# LectorTraccion.py

import asyncio
import aiofiles
import threading
import serial
import time
import os
import re
from datetime import datetime
import traceback
import atexit
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class LectorSerial(threading.Thread):
    """
    Hilo dedicado a la lectura de datos desde el puerto serial y al disparo
    de la adquisición cuando se cumplen ciertas condiciones.
    Implementa escritura asíncrona, optimización de procesamiento de strings,
    manejo eficiente de memoria y paralelización de tareas de procesamiento.
    Maneja correctamente datos incompletos recibidos del puerto serial.
    """

    def __init__(
        self,
        callback_disparo_adquisicion,
        carpeta_lecturas,
        callback_fin_ensayo=None,
        puerto="COM8",
        baudrate=9600,
        max_lecturas_en_memoria=1000
    ):
        """
        Inicializa el lector serial.

        Parámetros:
        - callback_disparo_adquisicion: Función a llamar cuando se dispara la adquisición.
        - carpeta_lecturas: Ruta a la carpeta donde se guardarán las lecturas.
        - callback_fin_ensayo: Función a llamar cuando el ensayo ha finalizado.
        - puerto: Nombre del puerto serial.
        - baudrate: Baudrate para la comunicación serial.
        - max_lecturas_en_memoria: Número máximo de lecturas a almacenar en memoria antes de guardar.
        """
        super().__init__()
        self.puerto = puerto
        self.baudrate = baudrate
        self.callback_disparo_adquisicion = callback_disparo_adquisicion
        self.callback_fin_ensayo = callback_fin_ensayo
        self.carpeta_lecturas = carpeta_lecturas
        self.max_lecturas_en_memoria = max_lecturas_en_memoria
        self.ser = None
        self.buffer = ""
        self.lecturas = []
        self.evento_detener = threading.Event()
        self.loop = asyncio.new_event_loop()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.patron_lectura = re.compile(r'\{([^}]*)\}')  # Ajuste para manejar datos incompletos
        atexit.register(self.cerrar_puerto_serial)

    def run(self):
        """
        Método principal del hilo que inicializa el bucle de eventos y comienza
        la lectura serial de manera asíncrona.
        """
        try:
            self.ser = serial.Serial(
                port=self.puerto,
                baudrate=self.baudrate,
                timeout=0
            )
            logging.info(f"Conectado al puerto {self.puerto} con baudrate {self.baudrate}.")

            asyncio.set_event_loop(self.loop)
            try:
                self.loop.run_until_complete(self.lectura_serial())
            except RuntimeError as e:
                if str(e) == 'Event loop stopped before Future completed.':
                    logging.warning(
                        "Bucle de eventos detenido antes de completar las tareas pendientes. Cerrando de forma controlada.")
                else:
                    raise e

        except serial.SerialException as e:
            logging.error(f"No se pudo abrir el puerto serial {self.puerto}: {e}")
        except Exception as e:
            logging.error(f"Error inesperado al iniciar el puerto serial: {e}")
            traceback.print_exc()
        finally:
            self.cerrar_puerto_serial()

    async def lectura_serial(self):
        """
        Método asíncrono para la lectura continua del puerto serial.
        Maneja correctamente los datos incompletos y los reconstruye.
        """
        try:
            while not self.evento_detener.is_set():
                try:
                    datos_bytes = self.ser.read(4096)  # Tamaño de búfer aumentado
                    if datos_bytes:
                        datos_str = datos_bytes.decode('utf-8', errors='ignore')
                        self.buffer += datos_str

                        # Procesar todas las lecturas completas en el buffer
                        while '{' in self.buffer and '}' in self.buffer:
                            inicio = self.buffer.find('{')
                            fin = self.buffer.find('}', inicio) + 1
                            if fin == 0:
                                # No se encontró un cierre '}', esperar más datos
                                break
                            lectura_completa = self.buffer[inicio:fin]
                            self.buffer = self.buffer[fin:]

                            # Extraer los datos dentro de las llaves
                            match = self.patron_lectura.match(lectura_completa)
                            if match:
                                datos = match.group(1).split(',')

                                if len(datos) > 3 and datos[3] == '0.000':
                                    if self.lecturas:
                                        await self.guardar_lecturas()
                                        if self.callback_fin_ensayo:
                                            self.callback_fin_ensayo()
                                    continue

                                self.lecturas.append(datos)
                                # Dispara la adquisición inmediatamente
                                self.callback_disparo_adquisicion(datos)

                                # Guardar lecturas para no acumular demasiadas en memoria
                                if len(self.lecturas) >= self.max_lecturas_en_memoria:
                                    await self.guardar_lecturas()
                            else:
                                # No es una lectura válida, continuar
                                continue

                        # Limitar el tamaño del buffer para evitar crecimiento excesivo
                        if len(self.buffer) > 10000:
                            self.buffer = self.buffer[-10000:]

                    else:
                        await asyncio.sleep(0.001)  # Pausa asincrónica mínima

                except serial.SerialException as e:
                    logging.error(f"Error en la comunicación serial: {e}")
                    break
                except Exception as e:
                    logging.error(f"Error inesperado en la lectura serial: {e}")
                    traceback.print_exc()
                    break

        except Exception as e:
            logging.error(f"Error en el bucle de lectura serial: {e}")
            traceback.print_exc()

    async def guardar_lecturas(self):
        """
        Guarda las lecturas acumuladas en un archivo de texto de forma asíncrona
        y libera memoria.
        """
        if not self.lecturas:
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = os.path.join(
                self.carpeta_lecturas, f"lecturas_{timestamp}.txt"
            )
            datos_a_guardar = "\n".join([",".join(lectura) for lectura in self.lecturas]) + "\n"

            # Enviar la tarea de escritura al executor
            self.executor.submit(asyncio.run, self.escritura_asincrona(datos_a_guardar, nombre_archivo))

            self.lecturas = []  # Liberar memoria después de guardar
            logging.info(f"Archivo de lecturas programado para guardar: {nombre_archivo}")
        except Exception as e:
            logging.error(f"Error al guardar las lecturas de forma asíncrona: {e}")
            traceback.print_exc()

    async def escritura_asincrona(self, datos_a_guardar, nombre_archivo):
        """
        Escribe los datos en disco de forma asíncrona.
        """
        try:
            async with aiofiles.open(nombre_archivo, "a", encoding='utf-8') as archivo:
                await archivo.write(datos_a_guardar)
            logging.info(f"Datos agregados a {nombre_archivo}")
        except Exception as e:
            logging.error(f"Error al escribir datos de forma asíncrona: {e}")
            traceback.print_exc()

    def cerrar_executor(self):
        """
        Cierra el ThreadPoolExecutor.
        """
        self.executor.shutdown(wait=True)
        logging.info("Executor cerrado correctamente.")

    def cerrar_puerto_serial(self):
        """
        Cierra el puerto serial si está abierto y el executor.
        """
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                logging.info(f"Puerto serial {self.puerto} cerrado correctamente.")
            except Exception as e:
                logging.error(f"Error al cerrar el puerto serial: {e}")
                traceback.print_exc()
        self.cerrar_executor()

    def detener(self):
        """
        Detiene el hilo de lectura y cierra el puerto serial.
        """
        self.evento_detener.set()
        self.loop.call_soon_threadsafe(self.loop.stop)
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
        baudrate=9600,
        max_lecturas_en_memoria=1000
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
