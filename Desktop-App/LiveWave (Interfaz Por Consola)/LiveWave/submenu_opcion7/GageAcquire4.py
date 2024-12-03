# =============================================================================
# Importaciones y configuración inicial
# =============================================================================

import sys
import time
import numpy as np
import GageSupport as gs
import GageConstants as gc

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

# =============================================================================
# Clase 2: ConfiguradorGage
# =============================================================================

class ConfiguradorGage:
    """
    Clase encargada de configurar el sistema, canales y disparadores.
    """

    def __init__(self, handle):
        self.handle = handle
        self.acq_config = {
            "SampleRate": 125000000,  # 125 MS/s
            "Depth": 8000,
            "Mode": gc.CS_MODE_OCT,
            "TriggerTimeout": 10000000,
            "SegmentSize": 8000,
            "TriggerHoldoff": 2000,
            "TriggerDelay": 0,
            "SampleResolution": 12
        }
        self.channel_config = {
            "InputRange": 10000,
            "Impedance": 50,  # Ohms
            "Coupling": gc.CS_COUPLING_DC,
            "DcOffset": 0,  # Sin offset
        }
        self.trigger_config = {
            "Level": 2,  # Porcentaje del rango de entrada
            "Source": 1,  # Canal 1
            "ExtCoupling": gc.CS_COUPLING_DC,
            "ExtRange": 2000,  # mV
        }

    def configurar(self):
        """
        Configura el sistema, los canales y los disparadores.
        """
        # Configuración de adquisición
        status = PyGage.SetAcquisitionConfig(self.handle, self.acq_config)
        if status < 0:
            raise RuntimeError(f"Error configurando adquisición: {PyGage.GetErrorString(status)}")

        # Obtener información del sistema
        system_info = PyGage.GetSystemInfo(self.handle)
        if not isinstance(system_info, dict):
            raise RuntimeError(f"Error obteniendo información del sistema: {PyGage.GetErrorString(system_info)}")

        print(f"Total de canales disponibles: {system_info['ChannelCount']}")  # Added debug statement

        # Configuración de canales
        # Configurar canales 1 y 5 (ajustar según disponibilidad)
        desired_channels = [1, 5]  # Cambiar a [1, 2] si el canal 5 no existe
        for channel in desired_channels:
            if channel > system_info['ChannelCount']:
                print(f"Advertencia: El canal {channel} no existe en este sistema.")
                continue
            status = PyGage.SetChannelConfig(self.handle, channel, self.channel_config)
            if status < 0:
                raise RuntimeError(f"Error configurando canal {channel}: {PyGage.GetErrorString(status)}")

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

    def adquirir(self, start_position, transfer_length):
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
            status = PyGage.GetStatus(self.handle)
            while status != gc.ACQ_STATUS_READY:
                status = PyGage.GetStatus(self.handle)
                # Removed ACQ_STATUS_ERROR check to prevent AttributeError
                time.sleep(0.01)  # Pequeña pausa para evitar consumo excesivo de CPU

            # Obtener información del sistema
            system_info = PyGage.GetSystemInfo(self.handle)
            if not isinstance(system_info, dict):
                raise RuntimeError(f"Error obteniendo información del sistema: {PyGage.GetErrorString(system_info)}")

            # Obtener configuración de adquisición
            acq = PyGage.GetAcquisitionConfig(self.handle)
            channel_increment = gs.CalculateChannelIndexIncrement(
                acq['Mode'],
                system_info['ChannelCount'],
                system_info['BoardCount']
            )

            # Adquirir datos de canales 1 y 5
            desired_channels = [1, 5]  # Cambiar a [1, 2] si el canal 5 no existe
            data_dict = {}
            for channel in desired_channels:
                if channel > system_info['ChannelCount']:
                    print(f"Advertencia: El canal {channel} no existe en este sistema.")
                    continue
                data_buffer = PyGage.TransferData(self.handle, channel, 0, 1, start_position, transfer_length)
                if isinstance(data_buffer, int):  # Si es un código de error
                    raise RuntimeError(f"Error transfiriendo datos del canal {channel}: {PyGage.GetErrorString(data_buffer)}")
                # Validate data_buffer[0]
                if not isinstance(data_buffer[0], (list, np.ndarray)):
                    print(f"Advertencia: Datos recibidos del canal {channel} no son válidos.")
                    continue
                data_dict[channel] = data_buffer[0]  # data_buffer[0] contiene los datos
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
            # Convert to numpy array for efficient computation
            muestras = np.array(muestras, dtype=np.float64)

            # Avoid division by zero
            if resolucion_adc == 0:
                raise ValueError("resolucion_adc cannot be zero.")

            scale_factor = rango_entrada / 2000.0
            offset = desplazamiento_dc / 1000.0

            # Calculate voltages
            voltajes = (((offset_muestra - muestras) / resolucion_adc) * scale_factor) + offset

            # Handle extremely large or small values
            # Replace inf with np.nan or some other placeholder
            voltajes = np.where(np.isfinite(voltajes), voltajes, np.nan)

            # Optionally, cap the values to a certain range
            max_voltage = rango_entrada / 1000.0  # Assuming maximum expected voltage
            min_voltage = -max_voltage
            voltajes = np.clip(voltajes, min_voltage, max_voltage)

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
    def guardar(filename, datos):
        """
        Guarda los datos en un archivo.
        """
        np.savetxt(filename, datos, delimiter=",", fmt="%.6f")
        print(f"Datos guardados en {filename}")

# =============================================================================
# Ejecución principal
# =============================================================================

if __name__ == "__main__":
    # Inicialización del sistema
    sistema = SistemaGage()
    try:
        sistema.inicializar()

        # Configuración
        configurador = ConfiguradorGage(sistema.handle)
        configurador.configurar()

        # Adquisición
        adquisidor = AdquisidorGage(sistema.handle)
        start_position = 0
        transfer_length = 2048
        data_dict = adquisidor.adquirir(start_position, transfer_length)

        if not data_dict:
            print("No se adquirieron datos.")
        else:
            # Conversión y guardado
            convertidor = ConvertidorVoltajes()
            for channel, data in data_dict.items():
                # Obtener configuración del canal
                chan_config = PyGage.GetChannelConfig(sistema.handle, channel)
                # Convertir datos a voltajes
                voltajes = convertidor.convertir(
                    data,
                    chan_config['InputRange'],
                    chan_config['DcOffset'],
                    2 ** (chan_config['Resolution']),
                    2 ** (chan_config['Resolution'] - 1)
                )
                # Guardar datos
                filename = f"data_ch{channel}.txt"
                GuardadorDatos.guardar(filename, voltajes)

    finally:
        sistema.liberar()
