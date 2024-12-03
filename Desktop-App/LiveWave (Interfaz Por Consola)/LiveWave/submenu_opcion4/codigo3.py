# -*- coding: utf-8 -*-
"""
Adaptado para calcular la amplitud y deformación usando un canal
"""

from __future__ import print_function
import time
import libtiepie

# Habilitar búsqueda de red
libtiepie.network.auto_detect_enabled = True

# Buscar dispositivos
libtiepie.device_list.update()

scp = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):
        scp = item.open_oscilloscope()
        if scp.measure_modes & libtiepie.MM_BLOCK:
            break
        else:
            scp = None

if scp is None:
    print("No se encontró un osciloscopio compatible.")
    sys.exit()

# Configurar modo de medición
scp.measure_mode = libtiepie.MM_BLOCK

# Configurar frecuencia de muestreo
scp.sample_frequency = 1e9  # 1 GHz

# Configurar longitud de registro
scp.record_length = 1000  # 1000 muestras

# Configurar relación de pre-muestras
scp.pre_sample_ratio = 0  # 0 %

# Configurar canales
for ch in scp.channels:
    ch.enabled = True
    ch.range = 2  # 2 V
    ch.coupling = libtiepie.CK_DCV  # Voltaje DC

# Configurar tiempo de espera del disparador
scp.trigger_time_out = 100e-3  # 100 ms

# Deshabilitar todas las fuentes de disparo de canales
for ch in scp.channels:
    ch.trigger.enabled = False

# Configurar disparo del canal 1
ch = scp.channels[0]
ch.trigger.enabled = True
ch.trigger.kind = libtiepie.TK_RISINGEDGE  # Flanco ascendente
ch.trigger.levels[0] = 0.5  # 50 %
ch.trigger.hystereses[0] = 0.05  # 5 %

# Archivo para guardar datos
output_file = "deformacion_oscilloscope.txt"

# Loop para medir cada 200ms
try:
    with open(output_file, "w") as f:
        # Escribir encabezados de columnas
        f.write("Tiempo,Amplitud,Deformacion\n")

        while True:
            scp.start()

            # Esperar a que la medición se complete
            while not scp.is_data_ready:
                time.sleep(0.01)  # 10 ms para reducir consumo de CPU

            # Obtener datos del Canal 1
            data_channel_1 = scp.get_data()[0]  # Solo Canal 1

            # Calcular amplitud
            amplitude = max(data_channel_1) - min(data_channel_1)

            # Calcular deformación (por ejemplo, usando una fórmula genérica)
            deformation = amplitude / 2  # Ajusta según la fórmula específica

            # Guardar datos en el archivo con la marca de tiempo
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp},{amplitude},{deformation}\n")

            # Esperar 200ms antes de la siguiente medición
            time.sleep(0.2)
except KeyboardInterrupt:
    print("Mediciones detenidas por el usuario.")
finally:
    del scp
