import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def process_and_visualize_data(file_list, threshold=0.1, sample_rate=125e6):
    """
    Procesa archivos de datos y visualiza los datos utilizando Matplotlib.

    Parameters:
        file_list (list): Lista de archivos a procesar.
        threshold (float): Umbral para identificar el inicio y fin de la señal.
        sample_rate (float): Frecuencia de muestreo en Hz.
    """
    # Crear un DataFrame vacío para almacenar todos los datos
    data = pd.DataFrame()

    # Leer cada archivo y almacenar los datos en el DataFrame
    for i, file in enumerate(file_list):
        df = pd.read_csv(file, header=14)
        channel_data = df.iloc[:, 0].values  # Asumiendo que los datos están en la primera columna
        dt = 1 / sample_rate  # Paso de tiempo
        time = np.arange(0, len(channel_data)) * dt

        # Ajustar datos según el canal
        if 'CH5' in file:
            channel_data *= 1  # Ajuste específico para CH5, si aplica

        temp_df = pd.DataFrame({'Time': time, 'Amplitude': channel_data, 'Channel': f'CH{i+1}'})
        data = pd.concat([data, temp_df], ignore_index=True)

    # Identificar el punto de inicio y el punto de llegada de la señal
    start_index = np.argmax(data['Amplitude'] > threshold)
    end_index = len(data) - np.argmax(data['Amplitude'][::-1] > threshold) - 1

    # Calcular el tiempo de vuelo
    time_of_flight = data['Time'].iloc[end_index] - data['Time'].iloc[start_index]
    print(f'Tiempo de vuelo: {time_of_flight} segundos')

    # Crear la visualización con Matplotlib
    plt.figure(figsize=(10, 6))
    for channel in data['Channel'].unique():
        subset = data[data['Channel'] == channel]
        plt.plot(subset['Time'], subset['Amplitude'], label=channel)

    plt.title('Time vs Data Channels')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend(title='Channel')
    plt.grid(True)
    plt.tight_layout()

    # Mostrar tiempo de vuelo en el gráfico
    plt.figtext(0.15, 0.85, f'Tiempo de vuelo: {time_of_flight:.6f} s', fontsize=10, color='red')

    # Mostrar el gráfico
    plt.show()

def main():
    # Lista de archivos de texto
    file_list = ['Acquire_CH1.txt', 'Acquire_CH5.txt']
    process_and_visualize_data(file_list)
