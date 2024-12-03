# Disparador.py

import os
import time
import sys
import traceback
import logging
import atexit
import signal
import psutil
import threading
from threading import Lock
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# from threading import Thread, Event  # No se utilizan actualmente

# Importaciones necesarias (asegurar que los módulos estén disponibles)
# from LectorTraccion import LectorSerial  # Importar la clase LectorSerial desde LectorTraccion.py
from LectorTraccion import LectorSerial  # Asegurar que este módulo esté disponible
# from GageAcquire4 import SistemaGage, ConfiguradorGage, AdquisidorGage, ConvertidorVoltajes, GuardadorDatos
# from Procesamiento import AnalizadorDatos

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# =============================================================================
# Clase: GestorRecursos
# =============================================================================

class GestorRecursos:
    """
    Clase responsable de monitorear los recursos del sistema (almacenamiento, RAM y CPU)
    durante la ejecución del ensayo. Emite advertencias y errores basados en umbrales
    predefinidos para cada recurso, y genera reportes periódicos si está habilitado.
    """

    # Umbrales de monitoreo definidos como constantes (para futuras configuraciones)
    UMBRAL_DISCO_NIVEL_1 = 70  # Porcentaje
    UMBRAL_DISCO_NIVEL_2 = 85  # Porcentaje
    UMBRAL_DISCO_NIVEL_3 = 95  # Porcentaje

    UMBRAL_RAM_NIVEL_1 = 75  # Porcentaje
    UMBRAL_RAM_NIVEL_2 = 90  # Porcentaje
    UMBRAL_RAM_NIVEL_3 = 95  # Porcentaje

    UMBRAL_CPU = 90  # Porcentaje para picos

    INTERVALO_MONITOREO = 5  # Segundos

    # Configuración de correo electrónico (constantes, para futuras configuraciones desde .ini)
    ENVIAR_CORREOS = True  # Activar o desactivar el envío de correos
    SMTP_SERVIDOR = "smtp.gmail.com"
    SMTP_PUERTO = 587
    EMAIL_ORIGEN = "bastian.proboste108@gmail.com"
    EMAIL_CONTRASENA = "qpxq etid byfy tpne"
    EMAIL_DESTINO = "bastian.proboste108@gmail.com"

    # Intervalo de reactivación de envío de correos por tipo de error (en segundos)
    INTERVALO_REACTIVACION = 60     #20 * 60  # 20 minutos

    # Configuración para reportes periódicos
    HABILITAR_REPORTES = True  # Activar o desactivar los reportes periódicos
    INTERVALO_REPORTES = 20 #10 * 60  # Cada 10 minutos

    def __init__(self):
        self.hilo_monitoreo = threading.Thread(target=self._monitorear_recursos, daemon=True)
        self.hilo_reportes = threading.Thread(target=self._generar_reportes_periodicos, daemon=True)
        self.stop_event = threading.Event()

        # Contadores para picos de CPU
        self.picos_cpu = 0

        # Diccionario para llevar el registro del último envío por tipo de error
        self.ultimo_envio_error = {
            "disco": 0,
            "ram": 0,
            "cpu": 0
        }

        # Contador para picos de CPU
        self.contador_picos_cpu = 0

        # Variables para almacenar máximos de uso de CPU y RAM
        self.max_cpu_usage = 0
        self.max_ram_usage = 0

        # Variable para almacenar el log acumulado
        self.log_acumulado = []

        # Configurar un handler para capturar los logs
        self._setup_logging_handler()

        # Variables para manejar la duración del ensayo (a obtener de LectorTraccion en el futuro)
        self.tiempo_inicio_ensayo = time.time()
        # self.tiempo_inicio_ensayo = None  # Se dejará comentado para obtenerlo de LectorTraccion en el futuro

    def _setup_logging_handler(self):
        """
        Configura un handler para capturar los logs en una variable.
        """
        self.log_handler = logging.StreamHandler()
        self.log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(formatter)
        self.log_handler.emit = self._emit_log_record  # Reemplazamos el método emit
        logging.getLogger().addHandler(self.log_handler)

    def _emit_log_record(self, record):
        """
        Método para capturar cada registro de log en la variable log_acumulado.
        """
        msg = self.log_handler.format(record)
        self.log_acumulado.append(msg)

    def iniciar_monitoreo(self):
        """
        Inicia los hilos de monitoreo de recursos y reportes periódicos.
        """
        try:
            self.hilo_monitoreo.start()
            if self.HABILITAR_REPORTES:
                self.hilo_reportes.start()
            logging.info("Monitoreo de recursos iniciado.")
        except Exception as e:
            logging.error(f"ERROR AL INICIAR EL MONITOREO DE RECURSOS: {e}")
            traceback.print_exc()

    def detener_monitoreo(self):
        """
        Detiene los hilos de monitoreo de recursos y reportes de manera segura.
        """
        try:
            self.stop_event.set()
            self.hilo_monitoreo.join()
            if self.HABILITAR_REPORTES:
                self.hilo_reportes.join()
            logging.info("Monitoreo de recursos detenido.")
        except Exception as e:
            logging.error(f"ERROR AL DETENER EL MONITOREO DE RECURSOS: {e}")
            traceback.print_exc()

    def _monitorear_recursos(self):
        """
        Método interno que ejecuta el monitoreo de recursos en un bucle.
        """
        try:
            while not self.stop_event.is_set():
                self._monitorear_disco()
                self._monitorear_ram()
                self._monitorear_cpu()
                time.sleep(self.INTERVALO_MONITOREO)
        except Exception as e:
            logging.error(f"ERROR EN EL MONITOREO DE RECURSOS: {e}")
            traceback.print_exc()

    def _monitorear_disco(self):
        """
        Monitorea el uso del almacenamiento (disco) y emite advertencias según los umbrales.
        """
        try:
            uso_disco = psutil.disk_usage('/').percent
            logging.debug(f"Uso de disco: {uso_disco}%")

            if uso_disco >= self.UMBRAL_DISCO_NIVEL_3:
                mensaje = "ADVERTENCIA CRÍTICA: ALMACENAMIENTO CRÍTICO (>95% de uso). SE DETENDRÁ LA ESCRITURA DE DATOS."
                logging.error(mensaje)
                self._enviar_correo("Alerta Crítica de Almacenamiento", mensaje)
                # Aquí podrías implementar la lógica para detener la escritura de datos
            elif uso_disco >= self.UMBRAL_DISCO_NIVEL_2:
                mensaje = "ADVERTENCIA: ALMACENAMIENTO MUY BAJO (>85% de uso). RECOMENDABLE FINALIZAR EL ENSAYO Y BUSCAR MÁS ALMACENAMIENTO."
                logging.warning(mensaje)
                self._enviar_correo("Alerta de Almacenamiento Muy Bajo", mensaje)
            elif uso_disco >= self.UMBRAL_DISCO_NIVEL_1:
                mensaje = "ADVERTENCIA: ALMACENAMIENTO BAJO (>70% de uso)."
                logging.warning(mensaje)
                self._enviar_correo("Alerta de Almacenamiento Bajo", mensaje)
        except Exception as e:
            logging.error(f"ERROR AL MONITOREAR ALMACENAMIENTO: {e}")
            traceback.print_exc()

    def _monitorear_ram(self):
        """
        Monitorea el uso de la memoria RAM y emite advertencias según los umbrales.
        """
        try:
            uso_ram = psutil.virtual_memory().percent
            logging.debug(f"Uso de RAM: {uso_ram}%")
            if uso_ram > self.max_ram_usage:
                self.max_ram_usage = uso_ram

            if uso_ram >= self.UMBRAL_RAM_NIVEL_3:
                mensaje = "ADVERTENCIA CRÍTICA: USO DE RAM CRÍTICO (>95%). POSIBLE FALLA EN EL ENSAYO."
                logging.error(mensaje)
                self._enviar_correo("Alerta Crítica de RAM", mensaje)
            elif uso_ram >= self.UMBRAL_RAM_NIVEL_2:
                mensaje = "ADVERTENCIA: USO DE RAM MUY ALTO (>90%). RECOMENDABLE OPTIMIZACIONES."
                logging.warning(mensaje)
                self._enviar_correo("Alerta de RAM Muy Alta", mensaje)
            elif uso_ram >= self.UMBRAL_RAM_NIVEL_1:
                mensaje = "ADVERTENCIA: USO DE RAM ALTO (>75%)."
                logging.warning(mensaje)
                self._enviar_correo("Alerta de RAM Alta", mensaje)
        except Exception as e:
            logging.error(f"ERROR AL MONITOREAR MEMORIA RAM: {e}")
            traceback.print_exc()

    def _monitorear_cpu(self):
        """
        Monitorea el uso del procesador (CPU) y emite advertencias según los umbrales.
        Detecta picos de uso y emite advertencias o errores críticos basados en la frecuencia de los picos.
        """
        try:
            uso_cpu = psutil.cpu_percent(interval=1)
            logging.debug(f"Uso de CPU: {uso_cpu}%")
            if uso_cpu > self.max_cpu_usage:
                self.max_cpu_usage = uso_cpu

            if uso_cpu > self.UMBRAL_CPU:
                self.contador_picos_cpu += 1
                mensaje = f"ADVERTENCIA: Pico de uso de CPU detectado ({uso_cpu}%)."
                logging.warning(mensaje)
                self._enviar_correo("Alerta de Pico de CPU", mensaje)

                if self.contador_picos_cpu == 3:
                    mensaje_error = "ERROR: Pico recurrente de uso de CPU (>90%). POSIBLE COMPROMISO DE DATOS."
                    logging.error(mensaje_error)
                    self._enviar_correo("Error de CPU Recurrente", mensaje_error)
                elif self.contador_picos_cpu >= 8:
                    mensaje_critico = "ERROR CRÍTICO: Pico continuo de uso de CPU (>90%). INTEGRIDAD DE DATOS COMPROMETIDA."
                    logging.critical(mensaje_critico)
                    self._enviar_correo("Error Crítico de CPU", mensaje_critico)
            else:
                self.contador_picos_cpu = 0  # Reiniciar contador si el uso de CPU está dentro de los límites
        except Exception as e:
            logging.error(f"ERROR AL MONITOREAR CPU: {e}")
            traceback.print_exc()

    def _generar_reportes_periodicos(self):
        """
        Método que genera y envía reportes periódicos cada INTERVALO_REPORTES segundos.
        """
        try:
            while not self.stop_event.is_set():
                time.sleep(self.INTERVALO_REPORTES)
                self._enviar_reporte()
        except Exception as e:
            logging.error(f"ERROR EN LA GENERACIÓN DE REPORTES PERIÓDICOS: {e}")
            traceback.print_exc()

    def _enviar_reporte(self):
        """
        Genera el reporte con el estado acumulado del ensayo y lo envía por correo.
        """
        try:
            # Construir el mensaje del reporte
            tiempo_actual = time.time()
            # duración_ensayo = tiempo_actual - self.tiempo_inicio_ensayo
            # Si el tiempo de inicio del ensayo se obtiene de LectorTraccion, se utilizará en el futuro

            timestamp_actual = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tiempo_actual))

            mensaje = f"REPORTE DEL ENSAYO\n"
            mensaje += f"Fecha y Hora: {timestamp_actual}\n"
            # mensaje += f"Duración del Ensayo: {duración_ensayo:.2f} segundos\n"
            mensaje += f"Máximo uso de CPU durante el ensayo: {self.max_cpu_usage}%\n"
            mensaje += f"Máximo uso de RAM durante el ensayo: {self.max_ram_usage}%\n\n"

            mensaje += "LOG ACUMULADO:\n"
            mensaje += "\n".join(self.log_acumulado)

            # Enviar el correo con el reporte
            asunto = "Reporte del Ensayo"
            self._enviar_correo(asunto, mensaje, es_reporte=True)

            logging.info("Reporte periódico enviado.")
        except Exception as e:
            logging.error(f"ERROR AL GENERAR O ENVIAR EL REPORTE: {e}")
            traceback.print_exc()

    def _enviar_correo(self, asunto, mensaje, es_reporte=False):
        """
        Envía un correo electrónico con el asunto y mensaje proporcionados.
        Implementa rate-limiting para evitar el spam.
        """
        if not self.ENVIAR_CORREOS:
            return

        if not es_reporte:
            tipo_error = ""
            if "Almacenamiento" in asunto:
                tipo_error = "disco"
            elif "RAM" in asunto:
                tipo_error = "ram"
            elif "CPU" in asunto:
                tipo_error = "cpu"

            tiempo_actual = time.time()
            tiempo_ultimo_envio = self.ultimo_envio_error.get(tipo_error, 0)

            if tiempo_actual - tiempo_ultimo_envio < self.INTERVALO_REACTIVACION:
                # No enviar correo si el intervalo no ha pasado
                return

            # Actualizar el último tiempo de envío
            self.ultimo_envio_error[tipo_error] = tiempo_actual

        # Enviar el correo en un hilo separado para no bloquear el monitoreo
        hilo_correo = threading.Thread(target=self._enviar_correo_thread, args=(asunto, mensaje), daemon=True)
        hilo_correo.start()

    def _enviar_correo_thread(self, asunto, mensaje):
        """
        Método que maneja el envío de correo en un hilo separado.
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = self.EMAIL_ORIGEN
            msg["To"] = self.EMAIL_DESTINO
            msg["Subject"] = asunto

            msg.attach(MIMEText(mensaje, "plain"))

            with smtplib.SMTP(self.SMTP_SERVIDOR, self.SMTP_PUERTO) as servidor:
                servidor.starttls()  # Iniciar la conexión segura
                servidor.login(self.EMAIL_ORIGEN, self.EMAIL_CONTRASENA)  # Iniciar sesión
                servidor.sendmail(self.EMAIL_ORIGEN, self.EMAIL_DESTINO, msg.as_string())

            logging.info(f"Correo enviado: {asunto}")
        except Exception as e:
            logging.error(f"ERROR AL ENVIAR CORREO: {e}")
            traceback.print_exc()

    def enviar_resumen(self, resumen):
        """
        Envía un correo de resumen al finalizar el ensayo.
        """
        if not self.ENVIAR_CORREOS:
            return

        asunto = "Resumen del Ensayo"
        mensaje = resumen

        # Enviar el correo en un hilo separado para no bloquear el monitoreo
        hilo_correo = threading.Thread(target=self._enviar_correo_thread, args=(asunto, mensaje), daemon=True)
        hilo_correo.start()

# =============================================================================
# Clase: GestorEnsayo
# =============================================================================

class GestorEnsayo:
    """
    Clase responsable de configurar el entorno del ensayo (carpetas y estructura).
    """

    def __init__(self):
        # Formato de timestamp más legible: "ensayo_2023-11-28_23-58-07"
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.base_folder = f"ensayo_{self.timestamp}"
        self.raw_folder = os.path.join(self.base_folder, "RAW")
        self.voltages_folder = os.path.join(self.base_folder, "Voltajes")
        self.calculaciones_folder = os.path.join(self.base_folder, "Calculaciones")

        # Lista para almacenar los directorios que no pudieron ser creados
        errores_creacion = []

        # Intentar crear cada directorio individualmente
        try:
            os.makedirs(self.raw_folder, exist_ok=True)
            logging.info(f"Directorio creado: {self.raw_folder}")
        except Exception as e:
            errores_creacion.append(f"RAW ({self.raw_folder})")
            logging.error(f"ERROR CRÍTICO: NO SE PUDO CREAR EL DIRECTORIO RAW: {e}")

        try:
            os.makedirs(self.voltages_folder, exist_ok=True)
            logging.info(f"Directorio creado: {self.voltages_folder}")
        except Exception as e:
            errores_creacion.append(f"Voltajes ({self.voltages_folder})")
            logging.error(f"ERROR CRÍTICO: NO SE PUDO CREAR EL DIRECTORIO Voltajes: {e}")

        try:
            os.makedirs(self.calculaciones_folder, exist_ok=True)
            logging.info(f"Directorio creado: {self.calculaciones_folder}")
        except Exception as e:
            errores_creacion.append(f"Calculaciones ({self.calculaciones_folder})")
            logging.error(f"ERROR CRÍTICO: NO SE PUDO CREAR EL DIRECTORIO Calculaciones: {e}")

        # Verificar si hubo errores en la creación de directorios
        if errores_creacion:
            if len(errores_creacion) == 3:
                logging.error("ERROR CRÍTICO: NO SE PUDIERON CREAR NINGUNO DE LOS DIRECTORIOS. EL ENSAYO NO PUEDE CONTINUAR.")
            else:
                directorios_fallidos = ", ".join(errores_creacion)
                logging.error(f"ERROR CRÍTICO: NO SE PUDIERON CREAR LOS SIGUIENTES DIRECTORIOS: {directorios_fallidos}. SE OMITE EL GUARDADO DE DATOS.")
            # Opcional: Aquí podrías lanzar una excepción para detener el programa si es crítico
            # raise Exception("Fallo en la creación de directorios.")
        else:
            logging.info(f"Todos los directorios fueron creados exitosamente para el ensayo: {self.base_folder}")

        # Placeholder para gestionar espacio de almacenamiento en el futuro
        # self.verificar_espacio_disponible()

    def verificar_espacio_disponible(self):
        """
        Método para verificar el espacio de almacenamiento disponible.
        """
        try:
            total, usado, libre = shutil.disk_usage(self.base_folder)
            espacio_libre_gigabytes = libre / (2**30)
            if espacio_libre_gigabytes < 1:  # Umbral de ejemplo: menos de 1 GB libre
                logging.warning("ADVERTENCIA: ESPACIO DE ALMACENAMIENTO BAJO. SE PUEDE PRODUCIR FALLA AL GUARDAR DATOS.")
            else:
                logging.info(f"Espacio de almacenamiento disponible: {espacio_libre_gigabytes:.2f} GB.")
        except Exception as e:
            logging.error(f"ERROR: NO SE PUDO VERIFICAR EL ESPACIO DE ALMACENAMIENTO: {e}")
            traceback.print_exc()

    # Puedes llamar a self.verificar_espacio_disponible() en el __init__ si lo deseas
    # self.verificar_espacio_disponible()


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
                logging.error("ERROR CRÍTICO: NINGUNO DE LOS CANALES ESTÁ RECIBIENDO DATOS VÁLIDOS. ADQUISICIÓN"
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
    import atexit
    import signal
    import psutil  # Asegúrate de tener psutil instalado
    import logging
    from threading import Lock
    # Asegúrate de importar las clases necesarias:
    # from Disparador import GestorEnsayo, ControladorAdquisicion, GestorRecursos, ControladorSerial

    # Configurar los intervalos para pruebas (por ejemplo, 10 segundos)
    GestorRecursos.INTERVALO_REACTIVACION = 60  # 1 minuto para pruebas
    GestorRecursos.INTERVALO_REPORTES = 30      # 30 segundos para pruebas
    GestorRecursos.HABILITAR_REPORTES = True    # Activar reportes para pruebas

    ensayo = GestorEnsayo()
    controlador_adquisicion = ControladorAdquisicion(ensayo)
    procesamiento_iniciado = False
    procesamiento_lock = Lock()

    gestor_recursos = GestorRecursos()

    # Definir el callback para disparo adquisición con print
    def callback_disparo_dummy(datos):
        """
        Función de callback que imprime y procesa los datos recibidos.
        """
        print(f"Callback disparo adquisición: {datos}")  # Print para debugging
        logging.info(f"Datos recibidos: {datos}")
        controlador_adquisicion.run_acquisition_once(datos)

    # Definir el callback para fin de ensayo
    def ensayo_fin_callback():
        nonlocal procesamiento_iniciado
        try:
            with procesamiento_lock:
                if not procesamiento_iniciado:
                    procesamiento_iniciado = True
                    logging.info("Ensayo finalizado. Iniciando procesamiento de datos.")
                    # Iniciar procesamiento de datos (comentar si no está disponible)
                    # analizador = AnalizadorDatos(
                    #     controlador_adquisicion.voltages_folder,
                    #     ensayo.calculaciones_folder
                    # )
                    # analizador.start()
                    # analizador.join()
                    logging.info("Procesamiento de datos completado.")

                    # Enviar resumen del ensayo
                    resumen = "El ensayo ha finalizado correctamente.\n"
                    resumen += f"Duración del ensayo: ...\n"  # Puedes agregar más información aquí
                    gestor_recursos.enviar_resumen(resumen)
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
            controlador_adquisicion.liberar_recursos()
            gestor_recursos.detener_monitoreo()
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
        print("4. Debug Correo")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            # Iniciar adquisición
            try:
                gestor_recursos.iniciar_monitoreo()

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
                gestor_recursos.iniciar_monitoreo()

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
            # Debug Correo
            try:
                # Enviar un correo de prueba con el estado actual del sistema
                uso_cpu = psutil.cpu_percent(interval=1)
                uso_ram = psutil.virtual_memory().percent

                mensaje = "REPORTE DE DEBUG\n"
                mensaje += f"Uso actual de CPU: {uso_cpu}%\n"
                mensaje += f"Uso actual de RAM: {uso_ram}%\n"

                # Enviar correo (asegúrate de que gestor_recursos esté inicializado)
                gestor_recursos._enviar_correo("Debug Correo - Estado Actual del Sistema", mensaje, es_reporte=True)
                logging.info("Correo de debug enviado.")
            except Exception as e:
                logging.error(f"Error al enviar correo de debug: {e}")
                traceback.print_exc()
        elif opcion == '5':
            logging.info("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción del menú.")

    logging.info("Programa finalizado correctamente.")


if __name__ == "__main__":
    main()
