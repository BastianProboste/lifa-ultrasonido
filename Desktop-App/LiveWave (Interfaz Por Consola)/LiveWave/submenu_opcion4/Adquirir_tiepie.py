
import os
import time
import sys
import traceback
import logging
import atexit
import signal
from threading import Lock
from datetime import datetime
# from threading import Thread, Event  # No se utilizan actualmente
from .TiePieController import ControladorTiePie
import threading

# Importaciones necesarias (asegurar que los módulos estén disponibles)
# from LectorTraccion import LectorSerial  # Importar la clase LectorSerial desde LectorTraccion.py
from LectorTraccion import LectorSerial  # Asegurar que este módulo esté disponible
# from GageAcquire4 import SistemaGage, ConfiguradorGage, AdquisidorGage, ConvertidorVoltajes, GuardadorDatos
# from Procesamiento import AnalizadorDatos

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# =============================================================================
# Clase: GestorEnsayo
# =============================================================================

class GestorEnsayo:
    """
    Clase responsable de configurar el entorno del ensayo (carpetas y estructura).
    """
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_folder = f"ensayo_{self.timestamp}"
        self.raw_folder = os.path.join(self.base_folder, "RAW")
        self.voltages_folder = os.path.join(self.base_folder, "Voltajes")
        self.calculaciones_folder = os.path.join(self.base_folder, "Calculaciones")

        try:
            os.makedirs(self.raw_folder, exist_ok=True)
            os.makedirs(self.voltages_folder, exist_ok=True)
            os.makedirs(self.calculaciones_folder, exist_ok=True)
            logging.info(f"Directorios creados para el ensayo: {self.base_folder}")
        except Exception as e:
            logging.error(f"Error al crear los directorios del ensayo: {e}")
            traceback.print_exc()


# =============================================================================
# Clase: ControladorAdquisicion
# =============================================================================

class ControladorAdquisicion:
    """
    Clase responsable del flujo de adquisición y procesamiento de datos.
    """

    def __init__(self, ensayo):
        self.lock_escritura = Lock()
        self.data_to_write = []
        self.ensayo = ensayo
        self.sistema = None
        self.configurador = None
        self.adquisidor = None
        self.convertidor = None

        # Inicializar sistema de adquisición
        try:
            # Comentar las siguientes líneas si las clases no están disponibles
            # self.sistema = SistemaGage()
            # self.sistema.inicializar()
            # self.configurador = ConfiguradorGage(self.sistema.handle)
            # self.configurador.configurar()
            # self.adquisidor = AdquisidorGage(self.sistema.handle)
            # self.convertidor = ConvertidorVoltajes()
            logging.info("Sistema de adquisición inicializado correctamente.")
        except Exception as e:
            logging.error(f"Error al inicializar el sistema de adquisición: {e}")
            traceback.print_exc()

        # Crear carpetas para RAW y Voltajes
        self.raw_folder = self.ensayo.raw_folder
        self.voltages_folder = self.ensayo.voltages_folder

    def run_acquisition_once(self, datos):
        """
        Realiza una adquisición completa, convierte a voltajes y guarda datos.
        """
        try:
            start_time = time.time()

            # Simular datos para pruebas o adquirirlos si es posible
            # data_dict = self.adquisidor.adquirir(0, 2048)
            data_dict = {}  # Placeholder para pruebas sin hardware

            end_time = time.time()

            # Obtener los datos de los canales
            data_ch1 = data_dict.get(1)
            data_ch2 = data_dict.get(5)  # Ajustar según los canales disponibles

            # Validar datos adquiridos por canal
            canales_invalidos = []

            # Validación para Canal 1
            if not isinstance(data_ch1, (list, tuple)):
                logging.warning("ADVERTENCIA: CANAL 1 NO ESTÁ RECIBIENDO DATOS O DATOS NO VÁLIDOS.")
                canales_invalidos.append(1)
            elif not data_ch1:
                logging.warning("ADVERTENCIA: CANAL 1 NO ESTÁ RECIBIENDO DATOS (DATA VACÍA).")
                canales_invalidos.append(1)
            else:
                # Aquí puedes agregar validaciones adicionales para data_ch1 si es necesario
                pass

            # Validación para Canal 2
            if not isinstance(data_ch2, (list, tuple)):
                logging.warning("ADVERTENCIA: CANAL 2 NO ESTÁ RECIBIENDO DATOS O DATOS NO VÁLIDOS.")
                canales_invalidos.append(2)
            elif not data_ch2:
                logging.warning("ADVERTENCIA: CANAL 2 NO ESTÁ RECIBIENDO DATOS (DATA VACÍA).")
                canales_invalidos.append(2)
            else:
                # Aquí puedes agregar validaciones adicionales para data_ch2 si es necesario
                pass

            # Si ambos canales son inválidos, omitir la adquisición
            if len(canales_invalidos) == 2:
                logging.error("ERROR CRÍTICO: NINGUNO DE LOS CANALES ESTÁ RECIBIENDO DATOS VÁLIDOS. ADQUISICIÓN "
                              "INCOMPLETA.")
                return

            # Convertir datos a voltajes para los canales válidos
            voltajes_ch1 = []
            voltajes_ch2 = []

            if 1 not in canales_invalidos:
                # Convertir datos a voltajes para Canal 1
                # voltajes_ch1 = self.convertidor.convertir(...)
                voltajes_ch1 = data_ch1  # Placeholder para pruebas
            else:
                logging.warning("ADVERTENCIA: NO SE PUEDE CONVERTIR DATOS DEL CANAL 1 POR FALTA DE DATOS VÁLIDOS.")

            if 2 not in canales_invalidos:
                # Convertir datos a voltajes para Canal 2
                # voltajes_ch2 = self.convertidor.convertir(...)
                voltajes_ch2 = data_ch2  # Placeholder para pruebas
            else:
                logging.warning("ADVERTENCIA: NO SE PUEDE CONVERTIR DATOS DEL CANAL 2 POR FALTA DE DATOS VÁLIDOS.")

            # Guardar datos RAW y Voltajes para los canales válidos
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")

            # Guardar datos RAW
            if 1 not in canales_invalidos and data_ch1:
                raw_ch1_file = os.path.join(self.raw_folder, f"CH1_RAW_{timestamp}.txt")
                # GuardadorDatos.guardar(raw_ch1_file, data_ch1)
                logging.info(f"Datos RAW del CANAL 1 guardados en {raw_ch1_file}.")
            else:
                logging.warning("ADVERTENCIA: NO SE GUARDARÁN DATOS RAW DEL CANAL 1.")

            if 2 not in canales_invalidos and data_ch2:
                raw_ch2_file = os.path.join(self.raw_folder, f"CH2_RAW_{timestamp}.txt")
                # GuardadorDatos.guardar(raw_ch2_file, data_ch2)
                logging.info(f"Datos RAW del CANAL 2 guardados en {raw_ch2_file}.")
            else:
                logging.warning("ADVERTENCIA: NO SE GUARDARÁN DATOS RAW DEL CANAL 2.")

            # Guardar datos de Voltajes
            if voltajes_ch1:
                volt_ch1_file = os.path.join(self.voltages_folder, f"CH1_Voltajes_{timestamp}.txt")
                # GuardadorDatos.guardar(volt_ch1_file, voltajes_ch1)
                logging.info(f"Datos de VOLTAJES del CANAL 1 guardados en {volt_ch1_file}.")
            else:
                logging.warning("ADVERTENCIA: NO SE GUARDARÁN DATOS DE VOLTAJES DEL CANAL 1.")

            if voltajes_ch2:
                volt_ch2_file = os.path.join(self.voltages_folder, f"CH2_Voltajes_{timestamp}.txt")
                # GuardadorDatos.guardar(volt_ch2_file, voltajes_ch2)
                logging.info(f"Datos de VOLTAJES del CANAL 2 guardados en {volt_ch2_file}.")
            else:
                logging.warning("ADVERTENCIA: NO SE GUARDARÁN DATOS DE VOLTAJES DEL CANAL 2.")

            # Guardar metadatos
            self.guardar_metadatos(start_time, end_time)

            logging.info(f"Adquisición realizada y datos guardados con timestamp {timestamp}.")

        except Exception as e:
            logging.error(f"Error durante la adquisición: {e}")
            traceback.print_exc()

    def liberar_recursos(self):
        """
        Libera los recursos del sistema de adquisición.
        """
        try:
            if self.sistema:
                self.sistema.liberar()
                logging.info("Recursos del sistema de adquisición liberados correctamente.")
        except Exception as e:
            logging.error(f"Error al liberar recursos: {e}")
            traceback.print_exc()

    def guardar_metadatos(self, start_time, end_time):
        """
        Guarda los metadatos de la adquisición.
        """
        try:
            duration = end_time - start_time
            metadatos = {
                'Duración': f"{duration:.6f} segundos",
                # 'SampleRate': self.configurador.acq_config['SampleRate'],
                # 'Depth': self.configurador.acq_config['Depth'],
                # 'Mode': self.configurador.acq_config['Mode'],
                # 'TriggerTimeout': self.configurador.acq_config['TriggerTimeout'],
                # 'SegmentSize': self.configurador.acq_config['SegmentSize'],
                # 'TriggerHoldoff': self.configurador.acq_config['TriggerHoldoff'],
                # 'TriggerDelay': self.configurador.acq_config['TriggerDelay'],
                # 'ChannelConfig': self.configurador.channel_config,
                # 'TriggerConfig': self.configurador.trigger_config
            }
            # Guardar metadatos en ambas carpetas
            for folder in [self.raw_folder, self.voltages_folder]:
                meta_file = os.path.join(folder, "metadatos.txt")
                with open(meta_file, 'w', encoding='utf-8') as f:
                    for key, value in metadatos.items():
                        f.write(f"{key}: {value}\n")
                logging.info(f"Metadatos guardados en {meta_file}")
        except Exception as e:
            logging.error(f"Error al guardar metadatos: {e}")
            traceback.print_exc()


# =============================================================================
# Clase: EscritorDatos (No utilizada actualmente)
# =============================================================================

# class EscritorDatos:
#     """
#     Clase que maneja la escritura de datos adquiridos en archivos.
#     """
#     def __init__(self, controlador, folder):
#         self.controlador = controlador
#         self.folder = folder
#         self.stop_event = Event()
#
#     def escribir_datos(self):
#         """
#         Hilo que maneja la escritura de datos en archivos.
#         """
#         while not self.stop_event.is_set():
#             if self.controlador.data_to_write:
#                 with self.controlador.lock_escritura:
#                     data_ch1, data_ch2 = self.controlador.data_to_write.pop(0)
#
#                 self.append_to_master("CH1_Master.txt", data_ch1)
#                 self.append_to_master("CH2_Master.txt", data_ch2)
#             else:
#                 time.sleep(0.1)
#
#     def append_to_master(self, filename, data):
#         """
#         Agrega datos al archivo correspondiente.
#         """
#         filepath = os.path.join(self.folder, filename)
#         with open(filepath, 'a', encoding='utf-8') as file:
#             file.write('\n'.join(map(str, data)) + '\n')
#         logging.info(f"Datos agregados a {filepath}")
#
#     def stop(self):
#         """
#         Detiene el hilo de escritura.
#         """
#         self.stop_event.set()


# =============================================================================
# Clase: ControladorSerial
# =============================================================================

class ControladorSerial:
    """
    Clase que maneja la lectura de datos desde el puerto serial.
    """
    def __init__(self,
                 callback_disparo_adquisicion,
                 carpeta_lecturas,
                 callback_fin_ensayo=None):
        try:
            self.lector_serial = LectorSerial(
                callback_disparo_adquisicion,
                carpeta_lecturas,
                callback_fin_ensayo
            )
            self.carpeta_lecturas = carpeta_lecturas
            self.callback_fin_ensayo = callback_fin_ensayo
            logging.info("Controlador serial inicializado correctamente.")
        except Exception as e:
            logging.error(f"Error al inicializar el controlador serial: {e}")
            traceback.print_exc()

    def iniciar(self):
        """
        Inicia la lectura desde el puerto serial.
        """
        try:
            self.lector_serial.start()
            logging.info("Lectura serial iniciada.")
        except Exception as e:
            logging.error(f"Error al iniciar la lectura serial: {e}")
            traceback.print_exc()

    def detener(self):
        """
        Detiene la lectura desde el puerto serial.
        """
        try:
            self.lector_serial.detener()
            self.lector_serial.join()
            logging.info("Lectura serial detenida.")
        except Exception as e:
            logging.error(f"Error al detener la lectura serial: {e}")
            traceback.print_exc()


# =============================================================================
# Programa Principal
# =============================================================================

def main():
    """
    Función principal que muestra un menú para ejecutar el programa.
    """
    ensayo = GestorEnsayo()
    controlador_adquisicion = ControladorAdquisicion(ensayo)
    procesamiento_iniciado = False
    procesamiento_lock = Lock()

    # Crear evento compartido para el trigger
    trigger_event = threading.Event()

    # Inicializar controlador TiePie
    tiepie_controller = ControladorTiePie(trigger_event, output_folder=ensayo.raw_folder)

    # Definir el callback para disparo adquisición con el trigger
    def callback_disparo_dummy(datos):
        """
        Función de callback que activa el trigger para ambas adquisiciones.
        """
        logging.info("Callback disparo activado.")
        trigger_event.set()  # Activar el trigger para TiePie
        trigger_event.clear()  # Reiniciar evento para la próxima adquisición
        controlador_adquisicion.run_acquisition_once(datos)  # Llamar adquisición del sistema principal

    # Definir el callback para fin de ensayo
    def ensayo_fin_callback():
        nonlocal procesamiento_iniciado
        try:
            with procesamiento_lock:
                if not procesamiento_iniciado:
                    procesamiento_iniciado = True
                    logging.info("Ensayo finalizado. Iniciando procesamiento de datos.")
                    # Iniciar procesamiento de datos (si está implementado)
                    # analizador = AnalizadorDatos(
                    #     controlador_adquisicion.voltages_folder,
                    #     ensayo.calculaciones_folder
                    # )
                    # analizador.start()
                    # analizador.join()
                    logging.info("Procesamiento de datos completado.")
        except Exception as e:
            logging.error(f"Error en ensayo_fin_callback: {e}")
            traceback.print_exc()
            close_resources()

    # Función para cerrar recursos
    def close_resources():
        """
        Función para cerrar recursos y liberar recursos de forma segura.
        """
        try:
            logging.info("Cerrando recursos y liberando recursos...")
            if 'serial_controller' in locals():
                serial_controller.detener()
            tiepie_controller.detener()  # Detener el hilo de TiePie
            controlador_adquisicion.liberar_recursos()  # Liberar recursos del sistema principal
            logging.info("Recursos cerrados y liberados correctamente.")
        except Exception as e:
            logging.error(f"Error al cerrar recursos: {e}")
            traceback.print_exc()

    # Registrar la función de cierre al finalizar el programa
    atexit.register(close_resources)

    # Manejar señales de interrupción
    def handle_signal(signum, frame):
        logging.info(f"Señal {signum} recibida. Cerrando recursos...")
        close_resources()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Menú principal
    while True:
        print("\nMenú Principal:")
        print("1. Ejecutar adquisición")
        print("2. Postprocesar datos")
        print("3. Ejecutar normalmente (sin GageAcquire4.py)")
        print("4. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            # Iniciar adquisición
            try:
                # Inicializar el controlador serial
                serial_controller = ControladorSerial(
                    callback_disparo_dummy,
                    ensayo.raw_folder,
                    callback_fin_ensayo=ensayo_fin_callback
                )
                serial_controller.iniciar()

                logging.info("Adquisición en curso. Presione Ctrl+C para detener.")
                while serial_controller.lector_serial.is_alive():
                    time.sleep(1)

            except KeyboardInterrupt:
                logging.info("Interrupción del usuario detectada. Cerrando...")
                serial_controller.detener()
            except Exception as e:
                logging.error(f"Error durante la adquisición: {e}")
                traceback.print_exc()
                close_resources()
                sys.exit(1)
            finally:
                close_resources()
                logging.info("Adquisición finalizada.")
        elif opcion == '2':
            # Postprocesar datos (pendiente de implementación)
            logging.info("Funcionalidad de postprocesamiento aún no implementada.")
        elif opcion == '3':
            # Ejecutar normalmente sin GageAcquire4.py
            try:
                # Inicializar el controlador serial
                serial_controller = ControladorSerial(
                    callback_disparo_dummy,
                    ensayo.raw_folder,
                    callback_fin_ensayo=ensayo_fin_callback
                )
                serial_controller.iniciar()

                logging.info("Ejecución normal en curso. Presione Ctrl+C para detener.")
                while serial_controller.lector_serial.is_alive():
                    time.sleep(1)

            except KeyboardInterrupt:
                logging.info("Interrupción del usuario detectada. Cerrando...")
                serial_controller.detener()
            except Exception as e:
                logging.error(f"Error durante la ejecución normal: {e}")
                traceback.print_exc()
                close_resources()
                sys.exit(1)
            finally:
                close_resources()
                logging.info("Ejecución normal finalizada.")
        elif opcion == '4':
            logging.info("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción del menú.")

    logging.info("Programa finalizado correctamente.")


if __name__ == "__main__":
    main()