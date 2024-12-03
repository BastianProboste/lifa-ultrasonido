# Procesamiento.py

import os
import numpy as np
import threading

class AnalizadorDatos(threading.Thread):
    """
    Clase que realiza análisis de datos adquiridos.
    """

    def __init__(self, voltages_folder, calculaciones_folder):
        super().__init__()
        self.voltages_folder = voltages_folder
        self.calculaciones_folder = calculaciones_folder
        os.makedirs(self.calculaciones_folder, exist_ok=True)

    def run(self):
        """
        Hilo que procesa y analiza los datos adquiridos.
        """
        try:
            # Leer archivos de voltajes ordenados por timestamp
            volt_ch1_files = sorted([
                f for f in os.listdir(self.voltages_folder)
                if f.startswith('CH1_Voltajes') and f.endswith('.txt')
            ])
            volt_ch5_files = sorted([
                f for f in os.listdir(self.voltages_folder)
                if f.startswith('CH5_Voltajes') and f.endswith('.txt')
            ])

            # Asegurarse de que hay archivos correspondientes
            if len(volt_ch1_files) != len(volt_ch5_files):
                print("Advertencia: La cantidad de archivos de CH1 y CH5 no coincide.")
                # Puedes decidir cómo manejar esto según tus necesidades

            for ch1_file, ch5_file in zip(volt_ch1_files, volt_ch5_files):
                data_ch1 = np.loadtxt(os.path.join(self.voltages_folder, ch1_file))
                data_ch5 = np.loadtxt(os.path.join(self.voltages_folder, ch5_file))

                self.procesar_datos(data_ch1, data_ch5, ch1_file, ch5_file)
        except Exception as e:
            print(f"Error durante el procesamiento: {e}")

    def procesar_datos(self, data_ch1, data_ch5, ch1_filename, ch5_filename):
        """
        Procesa los datos adquiridos, calcula la convolución y guarda los resultados.
        """
        sample_rate = 125e6  # Ajustar si es necesario
        time_step = 1 / sample_rate

        try:
            # Calcular la convolución de los dos canales
            convolution_result = np.convolve(data_ch1, data_ch5, mode='full')
            peak_index = np.argmax(np.abs(convolution_result))
            time_of_flight = peak_index * time_step

            # Guardar resultados
            base_filename = os.path.splitext(ch1_filename)[0].replace('CH1_Voltajes_', '')

            # Guardar tiempo de vuelo
            tiempos_vuelo_file = os.path.join(
                self.calculaciones_folder, f"tiempos_vuelo_{base_filename}.txt"
            )
            with open(tiempos_vuelo_file, "a") as file:
                file.write(f"{time_of_flight:.6e}\n")

            # Guardar datos de convolución
            datos_convolucion_file = os.path.join(
                self.calculaciones_folder, f"datos_convolucion_{base_filename}.txt"
            )
            np.savetxt(datos_convolucion_file, convolution_result, fmt="%.6f")

            print(f"Procesamiento completado para {base_filename}")
        except Exception as e:
            print(f"Error al procesar datos de {base_filename}: {e}")
