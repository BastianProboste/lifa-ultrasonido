# Controlador de Generador de Funciones Rigol DG1022

Este repositorio contiene un conjunto de funciones para controlar el generador de funciones Rigol DG1022. Permite configurar señales, consultar estados y controlar modos específicos, como el modo burst.

## Funciones

### 1. `set_gaussian_wave(frequency, cycles, amplitude_low)`
Establece la frecuencia y amplitud en el generador de funciones.

**Parámetros:**
- `frequency` (float): Frecuencia de salida en Hz.
- `cycles` (int): Voltaje máximo (HIGH) en V.
- `amplitude_low` (float): Voltaje mínimo (LOW) en V.

### 2. `get_burst_state()`
Consulta y devuelve el estado del modo ráfaga del generador.

### 3. `get_channel_state()`
Obtiene y muestra el estado del canal 1 del generador.

### 4. `control_burst_mode(enable_burst, num_cycles)`
Controla el modo burst del generador de funciones.

**Parámetros:**
- `enable_burst` (bool): Activar (True) o desactivar (False) el modo burst.
- `num_cycles` (int): Número de ciclos a configurar en el modo burst (solo si está activado).

### 5. `configure_sine_wave_signal()`
Configura una señal sinusoidal en el generador de funciones. Solicita al usuario la frecuencia, amplitud y offset.

### 6. `get_channel_configuration()`
Obtiene la configuración del canal seleccionado en el generador.

## Requisitos

- Python 3.x
- Librería `time` para pausas en la ejecución.
- Librería para la comunicación con el generador (asegúrate de tener la clase `dg1022` implementada y correctamente conectada).

## Uso

1. Asegúrate de que el generador de funciones Rigol DG1022 esté correctamente conectado.
2. Ejecuta el script de Python. El menú aparecerá en la consola.
3. Selecciona una opción ingresando el número correspondiente.
4. Clase dg1022 con funciones para manejo

```python
import time
from dg1022 import *  # Asegúrate de importar las funciones correctamente

# Ejemplo de uso
set_gaussian_wave(1000, 5, 0)  # Configurar onda gaussiana
get_burst_state()               # Consultar estado del modo burst