# GageAcquire.py

# =============================================================================
# Importaciones y configuración inicial
# =============================================================================

import sys
import time
import numpy as np

# Importar módulos de Gage (mantener en inglés según indicación)
import GageSupport as gs
import GageConstants as gc

# Determinar si el sistema es de 64 bits y la versión de Python
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
# Clase 1: SistemaGage
# =============================================================================

class SistemaGage:
    """
    Clase para manejar la inicialización y liberación del sistema PyGage.
    """

    def __init__(self):
        self.handle = None

    def __enter__(self):
        """
        Permite el uso de la clase con la sentencia 'with'.
        """
        self.inicializar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Garantiza que los recursos se liberen al salir del bloque 'with'.
        """
        self.liberar()

    def inicializar(self):
        """
        Inicializa el sistema PyGage y obtiene el handle necesario.
        """
        status = PyGage.Initialize()
        if status < 0:
            raise RuntimeError(f"Error al inicializar el sistema: {PyGage.GetErrorString(status)}")
        self.handle = PyGage.GetSystem(0, 0, 0, 0)
        print("Sistema inicializado correctamente.")

    def liberar(self):
        """
        Libera los recursos del sistema.
        """
        if self.handle is not None:
            PyGage.FreeSystem(self.handle)
            print("Sistema liberado.")
            self.handle = None

# =============================================================================
# Clase 2: ConfiguradorGage
# =============================================================================

class ConfiguradorGage:
    """
    Clase encargada de configurar el sistema, canales y disparadores.
    """

    # Configuraciones de adquisición por defecto
    CONFIGURACION_ADQUISICION_DEFECTO = {
        "SampleRate": 125000000,  # 125 MS/s
        "Depth": 8000,
        "Mode": gc.CS_MODE_OCT,
        "TriggerTimeout": 10000000,
        "SegmentSize": 8000,
        "TriggerHoldoff": 2000,
        "TriggerDelay": 0,
        "SampleResolution": 12
    }

    # Configuraciones de canal por defecto
    CONFIGURACION_CANAL_DEFECTO = {
        "InputRange": 10000,  # mV
        "Impedance": 50,      # Ohms
        "Coupling": gc.CS_COUPLING_DC,
        "DcOffset": 0,        # Sin offset
    }

    # Configuraciones de disparador por defecto
    CONFIGURACION_DISPARADOR_DEFECTO = {
        "Level": 2,           # Porcentaje del rango de entrada
        "Source": 1,          # Canal 1
        "ExtCoupling": gc.CS_COUPLING_DC,
        "ExtRange": 2000,     # mV
    }

    def __init__(self, handle):
        self.handle = handle
        self.acq_config = self.CONFIGURACION_ADQUISICION_DEFECTO.copy()
        self.channel_config = self.CONFIGURACION_CANAL_DEFECTO.copy()
        self.trigger_config = self.CONFIGURACION_DISPARADOR_DEFECTO.copy()

    def configurar(self):
        """
        Configura el sistema, los canales y los disparadores.
        """
        # Configuración de adquisición
        status = PyGage.SetAcquisitionConfig(self.handle, self.acq_config)
        if status < 0:
            raise RuntimeError(f"Error configurando adquisición: {PyGage.GetErrorString(status)}")

        # Obtener información del sistema
        info_sistema = PyGage.GetSystemInfo(self.handle)
        if not isinstance(info_sistema, dict):
            raise RuntimeError(f"Error obteniendo información del sistema: {PyGage.GetErrorString(info_sistema)}")

        print(f"Total de canales disponibles: {info_sistema['ChannelCount']}")

        # Configuración de canales
        # Configurar canales 1 y 5 (ajustar según disponibilidad)
        canales_deseados = [1, 5]  # Cambiar a [1, 2] si el canal 5 no existe
        for canal in canales_deseados:
            if canal > info_sistema['ChannelCount']:
                print(f"Advertencia: El canal {canal} no existe en este sistema.")
                continue
            status = PyGage.SetChannelConfig(self.handle, canal, self.channel_config)
            if status < 0:
                raise RuntimeError(f"Error configurando canal {canal}: {PyGage.GetErrorString(status)}")

        # Configuración de disparador
        status = PyGage.SetTriggerConfig(self.handle, 1, self.trigger_config)
        if status < 0:
            raise RuntimeError(f"Error configurando el disparador: {PyGage.GetErrorString(status)}")

        # Aplicar configuraciones
        status = PyGage.Commit(self.handle)
        if status < 0:
            raise RuntimeError(f"Error aplicando la configuración: {PyGage.GetErrorString(status)}")
        print("Sistema configurado correctamente.")

# =============================================================================
# Clase 3: AdquisidorGage
# =============================================================================

class AdquisidorGage:
    """
    Clase encargada de adquirir datos del sistema configurado.
    """

    def __init__(self, handle):
        self.handle = handle

    def adquirir(self, posicion_inicial, longitud_transferencia):
        """
        Adquiere los datos y los retorna en formato crudo.

        Retorna:
        - data_dict: Diccionario con clave canal y valor datos.
        En caso de error, retorna un diccionario vacío.
        """
        try:
            # Iniciar captura
            status = PyGage.StartCapture(self.handle)
            if status < 0:
                raise RuntimeError(f"Error iniciando captura: {PyGage.GetErrorString(status)}")

            # Esperar a que la captura se complete
            while True:
                status = PyGage.GetStatus(self.handle)
                if status == gc.ACQ_STATUS_READY:
                    break
                elif status == gc.ACQ_STATUS_BUSY:
                    time.sleep(0.01)  # Pequeña pausa para evitar consumo excesivo de CPU
                else:
                    raise RuntimeError(f"Error en el estado de adquisición: {PyGage.GetErrorString(status)}")

            # Obtener información del sistema
            info_sistema = PyGage.GetSystemInfo(self.handle)
            if not isinstance(info_sistema, dict):
                raise RuntimeError(f"Error obteniendo información del sistema: {PyGage.GetErrorString(info_sistema)}")

            # Adquirir datos de canales 1 y 5
            canales_deseados = [1, 5]  # Cambiar a [1, 2] si el canal 5 no existe
            data_dict = {}
            for canal in canales_deseados:
                if canal > info_sistema['ChannelCount']:
                    print(f"Advertencia: El canal {canal} no existe en este sistema.")
                    continue
                data_buffer = PyGage.TransferData(self.handle, canal, 0, 1, posicion_inicial, longitud_transferencia)
                if isinstance(data_buffer, int):  # Si es un código de error
                    raise RuntimeError(f"Error transfiriendo datos del canal {canal}: {PyGage.GetErrorString(data_buffer)}")
                # Validar data_buffer[0]
                if not isinstance(data_buffer[0], (list, np.ndarray)):
                    print(f"Advertencia: Datos recibidos del canal {canal} no son válidos.")
                    continue
                data_dict[canal] = data_buffer[0]  # data_buffer[0] contiene los datos
            return data_dict
        except RuntimeError as e:
            print(f"Error durante la adquisición: {e}")
            return {}  # Devuelve diccionario vacío en caso de error
        except Exception as e:
            print(f"Error inesperado durante la adquisición: {e}")
            return {}  # Devuelve diccionario vacío en caso de error

# =============================================================================
# Clase 4: ConvertidorVoltajes
# =============================================================================

class ConvertidorVoltajes:
    """
    Clase encargada de convertir datos digitales a voltajes.
    """

    @staticmethod
    def convertir(muestras, rango_entrada, desplazamiento_dc, resolucion_adc, offset_muestra):
        """
        Convierte datos digitales adquiridos en voltajes.
        """
        try:
            # Convertir a array de numpy para eficiencia
            muestras = np.array(muestras, dtype=np.float64)

            # Evitar división por cero
            if resolucion_adc == 0:
                raise ValueError("La resolución del ADC no puede ser cero.")

            factor_escala = rango_entrada / 2000.0
            offset = desplazamiento_dc / 1000.0

            # Calcular voltajes
            voltajes = (((offset_muestra - muestras) / resolucion_adc) * factor_escala) + offset

            # Manejar valores extremadamente grandes o pequeños
            voltajes = np.where(np.isfinite(voltajes), voltajes, np.nan)

            # Opcionalmente, limitar los valores a un rango específico
            voltaje_maximo = rango_entrada / 1000.0  # Voltaje máximo esperado
            voltaje_minimo = -voltaje_maximo
            voltajes = np.clip(voltajes, voltaje_minimo, voltaje_maximo)

            return voltajes.tolist()
        except Exception as e:
            print(f"Error en ConvertidorVoltajes.convertir: {e}")
            return []

# =============================================================================
# Clase 5: GuardadorDatos
# =============================================================================

class GuardadorDatos:
    """
    Clase encargada de guardar datos en archivos.
    """

    @staticmethod
    def guardar(nombre_archivo, datos):
        """
        Guarda los datos en un archivo.
        """
        np.savetxt(nombre_archivo, datos, delimiter=",", fmt="%.6f")
        print(f"Datos guardados en {nombre_archivo}")

# =============================================================================
# Ejecución principal
# =============================================================================

if __name__ == "__main__":
    # Inicialización del sistema usando contexto para asegurar liberación de recursos
    with SistemaGage() as sistema:
        try:
            # Configuración
            configurador = ConfiguradorGage(sistema.handle)
            configurador.configurar()

            # Adquisición
            adquisidor = AdquisidorGage(sistema.handle)
            posicion_inicial = 0
            longitud_transferencia = 2048
            data_dict = adquisidor.adquirir(posicion_inicial, longitud_transferencia)

            if not data_dict:
                print("No se adquirieron datos.")
            else:
                # Conversión y guardado
                convertidor = ConvertidorVoltajes()
                for canal, datos in data_dict.items():
                    # Obtener configuración del canal
                    config_canal = PyGage.GetChannelConfig(sistema.handle, canal)
                    # Convertir datos a voltajes
                    voltajes = convertidor.convertir(
                        datos,
                        config_canal['InputRange'],
                        config_canal['DcOffset'],
                        2 ** config_canal['Resolution'],
                        2 ** (config_canal['Resolution'] - 1)
                    )
                    # Guardar datos
                    nombre_archivo = f"data_ch{canal}.txt"
                    GuardadorDatos.guardar(nombre_archivo, voltajes)
        except Exception as e:
            print(f"Error durante la ejecución: {e}")
            # Si ocurre una excepción, se liberarán los recursos al salir del bloque 'with'
