import os
import time
import numpy as np
from datetime import datetime
from threading import Thread, Lock, Event
from traccion import *
from GageAcquire4 import *
from Procesamiento import *
import sys
import traceback
import atexit
import logging

is_64_bits = sys.maxsize > 2 ** 32
if is_64_bits:
    if sys.version_info >= (3, 0):
        import PyGage3_64 as PyGage
    else:
        import PyGage2_64 as PyGage
else:
    if sys.version_info >= (3, 0):
        import PyGage3_32 as PyGage
    else:
        import PyGage2_32 as PyGage

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
        self.voltages_folder = os.path.join(self.base_folder, "Voltages")
        self.calculaciones_folder = os.path.join(self.base_folder, "Calculaciones")
        os.makedirs(self.raw_folder, exist_ok=True)
        os.makedirs(self.voltages_folder, exist_ok=True)
        os.makedirs(self.calculaciones_folder, exist_ok=True)

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

        # Inicializar sistema de adquisición
        self.sistema = SistemaGage()
        self.sistema.inicializar()
        self.configurador = ConfiguradorGage(self.sistema.handle)
        self.configurador.configurar()
        self.adquisidor = AdquisidorGage(self.sistema.handle)
        self.convertidor = ConvertidorVoltajes()

        # Crear carpetas para RAW y Voltages
        #self.raw_folder = os.path.join(self.ensayo.base_folder, "RAW")
        #self.voltages_folder = os.path.join(self.ensayo.base_folder, "Voltages")
        #os.makedirs(self.raw_folder, exist_ok=True)
        #os.makedirs(self.voltages_folder, exist_ok=True)

        # Crear carpetas para RAW y Voltages
        self.raw_folder = self.ensayo.raw_folder
        self.voltages_folder = self.ensayo.voltages_folder
        os.makedirs(self.raw_folder, exist_ok=True)
        os.makedirs(self.voltages_folder, exist_ok=True)

    def run_acquisition_once(self, datos):
        """
        Realiza una adquisición completa, convierte a voltajes, y guarda datos.
        """
        start_time = time.time()
        data_dict = self.adquisidor.adquirir(0, 2048)
        end_time = time.time()

        # Obtener los datos de los canales
        data_ch1 = data_dict.get(1)
        data_ch2 = data_dict.get(5)  # Ajusted based on available channels

        # Validar datos adquiridos
        if not isinstance(data_ch1, (list, np.ndarray)) or not isinstance(data_ch2, (list, np.ndarray)):
            print("Error: Los datos adquiridos no son válidos.")
            return

        # Convertir datos a voltajes
        voltajes_ch1 = self.convertidor.convertir(
            data_ch1,
            self.configurador.channel_config['InputRange'],
            self.configurador.channel_config['DcOffset'],
            2 ** self.configurador.acq_config['SampleResolution'],
            2 ** (self.configurador.acq_config['SampleResolution'] - 1)
        )

        voltajes_ch2 = self.convertidor.convertir(
            data_ch2,
            self.configurador.channel_config['InputRange'],
            self.configurador.channel_config['DcOffset'],
            2 ** self.configurador.acq_config['SampleResolution'],
            2 ** (self.configurador.acq_config['SampleResolution'] - 1)
        )

        # Guardar datos RAW
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        raw_ch1_file = os.path.join(self.raw_folder, f"CH1_RAW_{timestamp}.txt")
        raw_ch2_file = os.path.join(self.raw_folder, f"CH2_RAW_{timestamp}.txt")
        GuardadorDatos.guardar(raw_ch1_file, data_ch1)
        GuardadorDatos.guardar(raw_ch2_file, data_ch2)

        # Guardar datos Voltajes
        volt_ch1_file = os.path.join(self.voltages_folder, f"CH1_Voltajes_{timestamp}.txt")
        volt_ch2_file = os.path.join(self.voltages_folder, f"CH2_Voltajes_{timestamp}.txt")
        GuardadorDatos.guardar(volt_ch1_file, voltajes_ch1)
        GuardadorDatos.guardar(volt_ch2_file, voltajes_ch2)

        # Guardar metadatos
        self.guardar_metadatos(start_time, end_time)

    def liberar_recursos(self):
        """
        Libera los recursos del sistema de adquisición.
        """
        self.sistema.liberar()

    def guardar_metadatos(self, start_time, end_time):
        """
        Guarda los metadatos de la adquisición.
        """
        duration = end_time - start_time
        metadatos = {
            'Duración': f"{duration:.6f} segundos",
            'SampleRate': self.configurador.acq_config['SampleRate'],
            'Depth': self.configurador.acq_config['Depth'],
            'Mode': self.configurador.acq_config['Mode'],
            'TriggerTimeout': self.configurador.acq_config['TriggerTimeout'],
            'SegmentSize': self.configurador.acq_config['SegmentSize'],
            'TriggerHoldoff': self.configurador.acq_config['TriggerHoldoff'],
            'TriggerDelay': self.configurador.acq_config['TriggerDelay'],
            'ChannelConfig': self.configurador.channel_config,
            'TriggerConfig': self.configurador.trigger_config
        }
        # Guardar metadatos en ambas carpetas
        for folder in [self.raw_folder, self.voltages_folder]:
            meta_file = os.path.join(folder, "metadatos.txt")
            with open(meta_file, 'w') as f:
                for key, value in metadatos.items():
                    f.write(f"{key}: {value}\n")
            print(f"Metadatos guardados en {meta_file}")

# =============================================================================
# Clase: EscritorDatos
# =============================================================================

class EscritorDatos:
    """
    Clase que maneja la escritura de datos adquiridos en archivos.
    """
    def __init__(self, controlador, folder):
        self.controlador = controlador
        self.folder = folder
        self.stop_event = Event()

    def escribir_datos(self):
        """
        Hilo que maneja la escritura de datos en archivos.
        """
        while not self.stop_event.is_set():
            if self.controlador.data_to_write:
                with self.controlador.lock_escritura:
                    data_ch1, data_ch2 = self.controlador.data_to_write.pop(0)

                self.append_to_master("CH1_Master.txt", data_ch1)
                self.append_to_master("CH2_Master.txt", data_ch2)
            else:
                time.sleep(0.1)

    def append_to_master(self, filename, data):
        """
        Agrega datos al archivo correspondiente.
        """
        filepath = os.path.join(self.folder, filename)
        with open(filepath, 'a') as file:
            file.write('\n'.join(map(str, data)) + '\n')
        print(f"Datos agregados a {filepath}")

    def stop(self):
        """
        Detiene el hilo de escritura.
        """
        self.stop_event.set()

# =============================================================================
# Clase: AnalizadorDatos
# =============================================================================


# =============================================================================
# Clase: ControladorSerial
# =============================================================================

class ControladorSerial:
    """
    Clase que maneja la lectura de datos desde el puerto serial.
    """
    def __init__(self, trigger_acquisition_callback, lecturas_folder, callback_ensayo_end=None):
        self.reader = SerialReader(trigger_acquisition_callback, lecturas_folder, callback_ensayo_end)
        self.lecturas_folder = lecturas_folder

    def iniciar(self):
        """
        Inicia la lectura desde el puerto serial.
        """
        self.reader.start()

    def detener(self):
        """
        Detiene la lectura desde el puerto serial.
        """
        self.reader.stop()
        self.reader.join()

# =============================================================================
# Programa Principal
# =============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    ensayo = GestorEnsayo()
    controlador_adquisicion = ControladorAdquisicion(ensayo)

    # Define a flag to prevent multiple processing threads
    procesamiento_iniciado = False
    procesamiento_lock = Lock()

    # Initialize the serial controller with the callback
    serial_controller = ControladorSerial(
        controlador_adquisicion.run_acquisition_once,
        ensayo.raw_folder,
        callback_ensayo_end=None  # Temporarily set to None
    )

    # Define the callback function for ensayo end
    def ensayo_end_callback():
        global procesamiento_iniciado
        try:
            with procesamiento_lock:
                if not procesamiento_iniciado:
                    procesamiento_iniciado = True
                    logging.info("Ensayo finalizado. Iniciando procesamiento de datos.")
                    # Start the AnalizadorDatos thread
                    analizador = AnalizadorDatos(
                        controlador_adquisicion.voltages_folder,
                        ensayo.calculaciones_folder
                    )
                    analizador.start()
                    analizador.join()
                    logging.info("Procesamiento de datos completado.")
        except Exception as e:
            logging.error(f"Error in ensayo_end_callback: {e}")
            traceback.print_exc()
            close_comports()

    # Assign the callback now that it's defined
    serial_controller.callback_ensayo_end = ensayo_end_callback

    def close_comports():
        """Function to safely close comports and release resources."""
        try:
            logging.info("Cerrando comports y liberando recursos...")
            serial_controller.detener()
            controlador_adquisicion.liberar_recursos()
            logging.info("Comports cerrados y recursos liberados correctamente.")
        except Exception as e:
            logging.error(f"Error al cerrar comports: {e}")
            traceback.print_exc()

    # Register the close_comports function to be called on program exit
    atexit.register(close_comports)

    # Additionally, ensure comports are closed on SIGTERM and SIGINT
    import signal

    def handle_signal(signum, frame):
        logging.info(f"Señal {signum} recibida. Cerrando comports...")
        close_comports()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Iniciar lectura serial
    try:
        serial_controller.iniciar()
    except Exception as e:
        logging.error(f"Error al iniciar el controlador serial: {e}")
        traceback.print_exc()
        close_comports()
        sys.exit(1)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Interrupción del usuario detectada. Cerrando...")
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        traceback.print_exc()
    finally:
        # Detener y unir hilos
        close_comports()
        logging.info("Adquisición finalizada. Si el ensayo no se ha terminado, iniciando procesamiento de datos.")

        # Check if processing was not started yet
        with procesamiento_lock:
            if not procesamiento_iniciado:
                try:
                    logging.info("Iniciando procesamiento de datos manualmente.")
                    analizador = AnalizadorDatos(
                        controlador_adquisicion.voltages_folder,
                        ensayo.calculaciones_folder
                    )
                    analizador.start()
                    analizador.join()
                    logging.info("Procesamiento de datos completado.")
                except Exception as e:
                    logging.error(f"Error durante el procesamiento de datos manual: {e}")
                    traceback.print_exc()
        logging.info("Todos los recursos han sido liberados correctamente.")

def trig_gag():
    ensayo = GestorEnsayo()
    controlador_adquisicion = ControladorAdquisicion(ensayo)

    # Define a flag to prevent multiple processing threads
    procesamiento_iniciado = False
    procesamiento_lock = Lock()

    # Initialize the serial controller with the callback
    serial_controller = ControladorSerial(
        controlador_adquisicion.run_acquisition_once,
        ensayo.raw_folder,
        callback_ensayo_end=None  # Temporarily set to None
    )
    def ensayo_end_callback():
        global procesamiento_iniciado
        try:
            with procesamiento_lock:
                if not procesamiento_iniciado:
                    procesamiento_iniciado = True
                    logging.info("Ensayo finalizado. Iniciando procesamiento de datos.")
                    # Start the AnalizadorDatos thread
                    analizador = AnalizadorDatos(
                        controlador_adquisicion.voltages_folder,
                        ensayo.calculaciones_folder
                    )
                    analizador.start()
                    analizador.join()
                    logging.info("Procesamiento de datos completado.")
        except Exception as e:
            logging.error(f"Error in ensayo_end_callback: {e}")
            traceback.print_exc()
            close_comports()

    # Assign the callback now that it's defined
    serial_controller.callback_ensayo_end = ensayo_end_callback

    def close_comports():
        """Function to safely close comports and release resources."""
        try:
            logging.info("Cerrando comports y liberando recursos...")
            serial_controller.detener()
            controlador_adquisicion.liberar_recursos()
            logging.info("Comports cerrados y recursos liberados correctamente.")
        except Exception as e:
            logging.error(f"Error al cerrar comports: {e}")
            traceback.print_exc()

    # Register the close_comports function to be called on program exit
    atexit.register(close_comports)

    # Additionally, ensure comports are closed on SIGTERM and SIGINT
    import signal

    def handle_signal(signum, frame):
        logging.info(f"Señal {signum} recibida. Cerrando comports...")
        close_comports()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Iniciar lectura serial
    try:
        serial_controller.iniciar()
    except Exception as e:
        logging.error(f"Error al iniciar el controlador serial: {e}")
        traceback.print_exc()
        close_comports()
        sys.exit(1)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Interrupción del usuario detectada. Cerrando...")
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        traceback.print_exc()
    finally:
        # Detener y unir hilos
        close_comports()
        logging.info("Adquisición finalizada. Si el ensayo no se ha terminado, iniciando procesamiento de datos.")

        # Check if processing was not started yet
        with procesamiento_lock:
            if not procesamiento_iniciado:
                try:
                    logging.info("Iniciando procesamiento de datos manualmente.")
                    analizador = AnalizadorDatos(
                        controlador_adquisicion.voltages_folder,
                        ensayo.calculaciones_folder
                    )
                    analizador.start()
                    analizador.join()
                    logging.info("Procesamiento de datos completado.")
                except Exception as e:
                    logging.error(f"Error durante el procesamiento de datos manual: {e}")
                    traceback.print_exc()
        logging.info("Todos los recursos han sido liberados correctamente.")    