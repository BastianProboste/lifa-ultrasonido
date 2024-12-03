import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html

# Lista de archivos de texto
file_list = ['Acquire_CH1.txt', 'Acquire_CH5.txt']  # Añade los nombres de los archivos aquí

# Crear un DataFrame vacío para almacenar todos los datos
data = pd.DataFrame()

# Leer cada archivo y almacenar los datos en el DataFrame
for i, file in enumerate(file_list):
    df = pd.read_csv(file, header=14)  # Asegúrate de que la lectura se hace correctamente
    channel_data = df.iloc[:, 0].values  # Asumiendo que los datos están en la primera columna
    dt = 1 / 125e6  # Paso de tiempo (125 MHz)
    time = np.arange(0, len(channel_data)) * dt
    
    # Si estamos procesando el archivo de CH5, multiplicamos los datos por 200
    if 'CH5' in file:
        channel_data *= 200  # Multiplicamos por 200 como mencionaste
    
    # Crear un DataFrame temporal para cada canal
    temp_df = pd.DataFrame({'Time': time, 'Amplitude': channel_data, 'Channel': f'CH{i+1}'})
    data = pd.concat([data, temp_df], ignore_index=True)

# Umbral para identificar el inicio y el final de la señal
threshold = 0.1  # Ajusta este valor según sea necesario

# Identificar el punto de inicio y el punto de llegada de la señal
start_index = np.argmax(data['Amplitude'] > threshold)
end_index = len(data) - np.argmax(data['Amplitude'][::-1] > threshold) - 1

# Calcular el tiempo de vuelo
time_of_flight = data['Time'].iloc[end_index] - data['Time'].iloc[start_index]

# Imprimir el tiempo de vuelo
print(f"Tiempo de vuelo: {time_of_flight} segundos")

# Crear una figura de Plotly
fig = px.line(data, x='Time', y='Amplitude', color='Channel',
              title='Time vs Data Channels', labels={'Amplitude': 'Amplitude', 'Channel': 'Channel'})

# Crear una aplicación Dash
app = Dash(__name__)

# Definir el layout de la aplicación
app.layout = html.Div(children=[
    html.H1(children='Gráfico de Datos de Acquire_CH1 y Acquire_CH5'),
    dcc.Graph(
        id='example-graph',
        figure=fig
    ),
    html.Div(f"Tiempo de vuelo calculado: {time_of_flight:.6f} segundos", style={'fontSize': 20, 'marginTop': 20})
])

if __name__ == '__main__':
    app.run_server(debug=True)
