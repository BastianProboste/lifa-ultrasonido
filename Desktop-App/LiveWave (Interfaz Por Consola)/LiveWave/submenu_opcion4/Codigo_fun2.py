# -*- coding: utf-8 -*-
"""
Adaptado para guardar datos en columnas por cada canal
"""

from __future__ import print_function
import time
import sys
import libtiepie

def setup_oscilloscope():
    """
    Configura el osciloscopio y lo retorna. Si no se encuentra un dispositivo compatible, termina el programa.
    """
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

    return scp

def save_data_to_file(scp, output_file="datos_oscilloscope_columns.txt"):
    """
    Realiza las mediciones y guarda los datos en un archivo.
    """
    try:
        with open(output_file, "w") as f:
            # Escribir encabezados de columnas
            channel_headers = [f"Canal {i + 1}" for i in range(len(scp.channels))]
            f.write("Tiempo," + ",".join(channel_headers) + "\n")

            while True:
                scp.start()

                # Esperar a que la medición se complete
                while not scp.is_data_ready:
                    time.sleep(0.01)  # 10 ms para reducir consumo de CPU

                # Obtener datos
                data = scp.get_data()

                # Guardar datos en columnas
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                for i in range(len(data[0])):  # Recorrer todas las muestras
                    row = [f"{timestamp}"] if i == 0 else [""]  # Solo incluir timestamp en la primera fila
                    for channel_data in data:  # Recorrer canales
                        row.append(str(channel_data[i]))
                    f.write(",".join(row) + "\n")

                # Esperar 200ms antes de la siguiente medición
                time.sleep(0.2)
    except KeyboardInterrupt:
        print("Mediciones detenidas por el usuario.")
    finally:
        del scp

def main():
    """
    Función principal que configura el osciloscopio y guarda los datos en un archivo.
    """
    # Configurar el osciloscopio
    scp = setup_oscilloscope()

    # Guardar los datos en un archivo
    save_data_to_file(scp)

if __name__ == "__main__":
    main()
