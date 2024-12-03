from __future__ import print_function
from builtins import int
import platform
import sys
from datetime import datetime
import GageSupport as gs
import GageConstants as gc
import os
# Obtener la ruta del directorio actual (donde está 'app.py')
directorio_actual = os.path.dirname(os.path.abspath(__file__))

# Crear la ruta completa para la carpeta 'módulos'
carpeta_modulos = os.path.join(directorio_actual, 'módulos')

# Agregar la carpeta 'módulos' al sys.path
sys.path.append(carpeta_modulos)
# Código utilizado para determinar si la versión de Python es 2.x o 3.x 
# y si el sistema operativo es de 32 bits o 64 bits. Si ya se conoce la versión
# de Python y el sistema operativo, se puede omitir esta parte e importar
# directamente la versión adecuada de la biblioteca.

# is_64_bits indica si Python es de 64 bits 
# (es decir, Python de 32 bits en Windows de 64 bits debería devolver False).
is_64_bits = sys.maxsize > 2**32

if is_64_bits:
    if sys.version_info >= (3, 0):
        import PyGage3_64 as PyGage
    else:
        import PyGage2_64 as PyGage
else:        
    if sys.version_info > (3, 0):
        import PyGage3_32 as PyGage 
    else:
        import PyGage2_32 as PyGage


def configure_system(handle, filename):
    # Configura el sistema de adquisición utilizando un archivo .ini
    acq, sts = gs.LoadAcquisitionConfiguration(handle, filename)	

    # Si se cargó correctamente la configuración de adquisición, se aplica.
    if isinstance(acq, dict) and acq:	
        status = PyGage.SetAcquisitionConfig(handle, acq)
        if status < 0:
            return status
    else:
        print("Usando parámetros predeterminados para la adquisición")

    # Comprueba si faltan parámetros en el archivo .ini
    if sts == gs.INI_FILE_MISSING:
        print("Archivo .ini no encontrado, usando valores predeterminados")
    elif sts == gs.PARAMETERS_MISSING:
        print("Faltan uno o más parámetros de adquisición, usando valores predeterminados")        
 
    system_info = PyGage.GetSystemInfo(handle)
    acq = PyGage.GetAcquisitionConfig(handle)  # verifica errores de configuración

    # Calcula el incremento de índice de canal según el modo de adquisición, 
    # el número de canales y el número de placas en el sistema.
    channel_increment = gs.CalculateChannelIndexIncrement(acq['Mode'], 
                                                          system_info['ChannelCount'], 
                                                          system_info['BoardCount'])	
	
    missing_parameters = False
    # Configura cada canal individualmente. 
    for i in range(1, system_info['ChannelCount'] + 1, channel_increment):
        chan, sts = gs.LoadChannelConfiguration(handle, i, filename)
        if isinstance(chan, dict) and chan:
            status = PyGage.SetChannelConfig(handle, i, chan)
            if status < 0:
                return status
        else:
            print("Usando parámetros predeterminados para el canal ", i)
        
        if sts == gs.PARAMETERS_MISSING:
            missing_parameters = True

    if missing_parameters:
        print("Faltan uno o más parámetros del canal, usando valores predeterminados")

    # Configura el disparador. En este ejemplo, solo se utiliza una fuente de disparo.
    trigger_count = 1
    for i in range(1, trigger_count + 1):
        trig, sts = gs.LoadTriggerConfiguration(handle, i, filename)
        if isinstance(trig, dict) and trig:
            status = PyGage.SetTriggerConfig(handle, i, trig)
            if status < 0:
                return status
        else:
            print("Usando parámetros predeterminados para el disparador ", i)

        if sts == gs.PARAMETERS_MISSING:
            missing_parameters = True

    if missing_parameters:
        print("Faltan uno o más parámetros del disparador, usando valores predeterminados")
		
    # Finaliza la configuración y la aplica
    status = PyGage.Commit(handle)
    return status
        

def initialize():
    # Inicializa el sistema de adquisición.
    status = PyGage.Initialize()
    if status < 0:
        return status
    else:
        handle = PyGage.GetSystem(0, 0, 0, 0)
        return handle		
        

def save_data_to_file(handle, mode, app, system_info):
    # Inicia la captura de datos.
    status = PyGage.StartCapture(handle)
    if status < 0:
        return status
        
    capture_time = 0        
    status = PyGage.GetStatus(handle)    
    while status != gc.ACQ_STATUS_READY:
        status = PyGage.GetStatus(handle)
        # Si el sistema ha recibido un disparo, toma la hora del día 
        # para almacenar la marca de tiempo en el archivo SIG
        if status == gc.ACQ_STATUS_TRIGGERED:
            capture_time = datetime.now().time() 

    # Si no se detectó el momento del disparo, usa la hora de captura
    if capture_time == 0: 
        capture_time = datetime.now().time()
    
    # Calcula el incremento de índice de canal
    channel_increment = gs.CalculateChannelIndexIncrement(mode, 
                                                          system_info['ChannelCount'], 
                                                          system_info['BoardCount'])

    # Obtiene la configuración de adquisición y valida la dirección de inicio y longitud
    acq = PyGage.GetAcquisitionConfig(handle)

    min_start_address = acq['TriggerDelay'] + acq['Depth'] - acq['SegmentSize']
    if app['StartPosition'] < min_start_address:
        print("\nLa dirección de inicio no es válida y se cambió de {0} a {1}".format(app['StartPosition'],  min_start_address))
        app['StartPosition'] = min_start_address

    max_length = acq['TriggerDelay'] + acq['Depth'] - min_start_address
    if app['TransferLength'] > max_length:
        print("\nLa longitud de transferencia no es válida y se cambió de {0} a {1}".format(app['TransferLength'], max_length))
        app['TransferLength'] = max_length

    # Configura el encabezado de almacenamiento de datos
    stHeader = {}
    if acq['ExternalClock']:
        stHeader['SampleRate'] = acq['SampleRate'] / acq['ExtClockSampleSkip'] * 1000
    else:
        stHeader['SampleRate'] = acq['SampleRate'] 

    stHeader['Start'] = app['StartPosition']
    stHeader['Length'] = app['TransferLength']
    stHeader['SampleSize'] = acq['SampleSize']
    stHeader['SampleOffset'] = acq['SampleOffset']
    stHeader['SampleRes'] = acq['SampleResolution']
    stHeader['SegmentNumber'] = 1  # solo captura única
    stHeader['SampleBits'] = acq['SampleBits']
    
    if app['SaveFileFormat'] == gs.TYPE_SIG:
        stHeader['SegmentCount'] = 1
    else:
        stHeader['SegmentCount'] = acq['SegmentCount']
    
    # Transfiere los datos de cada canal y los guarda en archivos
    for i in range(1, system_info['ChannelCount'] + 1, channel_increment):
        buffer = PyGage.TransferData(handle, i, 0, 1, app['StartPosition'], app['TransferLength'])
        if isinstance(buffer, int): # ocurrió un error
            print("Error al transferir datos del canal ", i)
            return buffer

        chan = PyGage.GetChannelConfig(handle, i)        
        stHeader['InputRange'] = chan['InputRange']
        stHeader['DcOffset'] = chan['DcOffset']

        if app['SaveFileFormat'] == gs.TYPE_SIG:
            filename = app['SaveFileName'] + '_CH' + str(i) + '.sig'
        elif app['SaveFileFormat'] == gs.TYPE_BIN:
            filename = app['SaveFileName'] + '_CH' + str(i) + '.dat'
        else:
            filename = app['SaveFileName'] + '_CH' + str(i) + '.txt'        

        # Ajusta la longitud del encabezado para reflejar la longitud de datos real en el buffer
        stHeader['Length'] = buffer[2]        

        # Agrega la marca de tiempo al encabezado
        timeStamp = {}
        timeStamp['Hour'] = capture_time.hour
        timeStamp['Minute'] = capture_time.minute
        timeStamp['Second'] = capture_time.second
        timeStamp['Point1Second'] = capture_time.microsecond // 1000 # convierte a milisegundos

        stHeader['TimeStamp'] = timeStamp
        status = gs.SaveFile(filename, i, buffer[0], app['SaveFileFormat'], stHeader)

    return status	
    

def main():
    # Archivo de configuración de la adquisición
    inifile = 'Acquire.ini'
    try:
        # Inicializa el sistema de adquisición
        handle = initialize()
        if handle < 0:
            error_string = PyGage.GetErrorString(handle)
            print("Error: ", error_string)
            raise SystemExit

        # Obtiene la información del sistema
        system_info = PyGage.GetSystemInfo(handle)
        if not isinstance(system_info, dict):
            print("Error: ", PyGage.GetErrorString(system_info))
            PyGage.FreeSystem(handle)
            raise SystemExit

        print("\nNombre de la placa: ", system_info["BoardName"])
        
        # Configura el sistema con el archivo .ini
        status = configure_system(handle, inifile)
        if status < 0:
            error_string = PyGage.GetErrorString(status)
            print("Error: ", error_string)
        else:
            acq_config = PyGage.GetAcquisitionConfig(handle)
            app, sts = gs.LoadApplicationConfiguration(inifile)	

            if sts == gs.PARAMETERS_MISSING:
                print("Faltan uno o más parámetros de aplicación, usando valores predeterminados")

            # Guarda los datos adquiridos en un archivo
            status = save_data_to_file(handle, acq_config['Mode'], app, system_info)
            if isinstance(status, int):
                if status < 0:
                    error_string = PyGage.GetErrorString(status)
                    print("Error: ", error_string)
                elif status == 0: 
                    print("Error al abrir o escribir ", filename)
                else:
                    if app['SaveFileFormat'] == gs.TYPE_SIG:
                        print("\nAdquisición completada.\nTodos los canales guardados como archivos SIG en el directorio actual\n")
                    elif app['SaveFileFormat'] == gs.TYPE_BIN:
                        print("\nAdquisición completada.\nTodos los canales guardados como archivos binarios en el directorio actual\n")
                    else:
                        print("\nAdquisición completada.\nTodos los canales guardados como archivos ASCII en el directorio actual\n")
            else:
                print("Error al abrir o escribir ", status)
    except KeyboardInterrupt:
        print("Saliendo del programa")

    PyGage.FreeSystem(handle) 
    

if __name__ == '__main__':
    main()
