import threading
import os
import time
import libtiepie
import logging
import traceback

# =============================================================================
# Clase: Controlador Osciloscopio
# =============================================================================
class ControladorTiePie(threading.Thread):
    """
    Clase independiente para manejar la adquisición con el osciloscopio `libtiepie`.
    Hereda de threading.Thread para ejecutar en un hilo separado.
    """
    def __init__(self, trigger_event, output_folder="TiePie_Output"):
        super().__init__()
        self.trigger_event = trigger_event  # Evento compartido para disparar adquisición
        self.output_folder = output_folder
        self.stop_event = threading.Event()
        self.scp = None
        self._initialize_hardware()

        # Crear carpeta para salida
        os.makedirs(self.output_folder, exist_ok=True)
        logging.info(f"Directorio de salida para TiePie: {self.output_folder}")

    def _initialize_hardware(self):
        """
        Inicializa y configura el osciloscopio TiePie.
        """
        try:
            libtiepie.network.auto_detect_enabled = True
            libtiepie.device_list.update()

            for item in libtiepie.device_list:
                if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):
                    self.scp = item.open_oscilloscope()
                    if self.scp.measure_modes & libtiepie.MM_BLOCK:
                        break
                    else:
                        self.scp = None

            if not self.scp:
                raise RuntimeError("No se encontró un osciloscopio compatible.")

            # Configuración del osciloscopio
            self.scp.measure_mode = libtiepie.MM_BLOCK
            self.scp.sample_frequency = 1e9  # 1 GHz
            self.scp.record_length = 1000  # 1000 muestras
            self.scp.pre_sample_ratio = 0  # 0 %
            self.scp.trigger_time_out = 100e-3  # 100 ms

            # Configurar canales
            for ch in self.scp.channels:
                ch.enabled = True
                ch.range = 2  # 2 V
                ch.coupling = libtiepie.CK_DCV  # Voltaje DC

            # Configurar trigger en el Canal 1
            ch = self.scp.channels[0]
            ch.trigger.enabled = True
            ch.trigger.kind = libtiepie.TK_RISINGEDGE  # Flanco ascendente
            ch.trigger.levels[0] = 0.5  # 50 %
            ch.trigger.hystereses[0] = 0.05  # 5 %

            logging.info("Osciloscopio TiePie configurado correctamente.")
        except Exception as e:
            logging.error(f"Error al inicializar TiePie: {e}")
            traceback.print_exc()

    def run(self):
        """
        Método principal del hilo: espera a que se active el trigger_event para adquirir datos.
        """
        try:
            while not self.stop_event.is_set():
                # Esperar activación del trigger_event
                if not self.trigger_event.wait(timeout=1):
                    continue

                logging.info("Trigger recibido, iniciando adquisición con TiePie.")
                self.adquirir_datos()

        except Exception as e:
            logging.error(f"Error en el hilo de TiePie: {e}")
            traceback.print_exc()
        finally:
            self.liberar_recursos()

    def adquirir_datos(self):
        """
        Realiza la adquisición de datos con el osciloscopio.
        """
        try:
            self.scp.start()

            # Esperar datos
            while not self.scp.is_data_ready:
                time.sleep(0.01)  # Reducir consumo de CPU

            # Obtener datos
            data_channel_1 = self.scp.get_data()[0]  # Canal 1
            amplitude = max(data_channel_1) - min(data_channel_1)
            deformation = amplitude / 2  # Fórmula de ejemplo

            # Guardar datos en archivo
            timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
            output_file = os.path.join(self.output_folder, "deformacion_oscilloscope.txt")
            with open(output_file, "a") as f:
                f.write(f"{timestamp},{amplitude},{deformation}\n")
            
            logging.info(f"Datos guardados en {output_file}.")
        except Exception as e:
            logging.error(f"Error durante la adquisición con TiePie: {e}")
            traceback.print_exc()

    def liberar_recursos(self):
        """
        Libera recursos del osciloscopio.
        """
        try:
            if self.scp:
                del self.scp
                logging.info("Recursos del TiePie liberados correctamente.")
        except Exception as e:
            logging.error(f"Error al liberar recursos de TiePie: {e}")
            traceback.print_exc()

    def detener(self):
        """
        Detiene el hilo y libera recursos.
        """
        self.stop_event.set()
        self.join()
        logging.info("Hilo de TiePie detenido.")

# ============================
# Ejemplo de uso integrado
# ============================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Evento compartido para disparar ambas adquisiciones
    trigger_event = threading.Event()

    # Inicializar y arrancar el hilo de TiePie
    tiepie_controller = ControladorTiePie(trigger_event)
    tiepie_controller.start()

    try:
        # Simular triggers externos
        while True:
            time.sleep(5)  # Espera de 5 segundos antes de activar el trigger
            logging.info("Activando trigger para adquisiciones.")
            trigger_event.set()
            trigger_event.clear()  # Resetear el evento después de activarlo

    except KeyboardInterrupt:
        logging.info("Interrupción del usuario. Cerrando...")
    finally:
        tiepie_controller.detener()