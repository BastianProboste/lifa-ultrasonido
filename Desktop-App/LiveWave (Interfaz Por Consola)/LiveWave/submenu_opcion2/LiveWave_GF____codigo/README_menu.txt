# Controlador del Generador de Funciones Rigol DG1022

Este módulo permite interactuar con el generador de funciones Rigol DG1022 a través de un menú interactivo en consola. Proporciona diversas opciones para configurar señales, consultar estados y controlar el generador.

## Contenido

- Menú de opciones para el usuario.
- Funciones para manejar diferentes configuraciones y estados del generador.

## Funciones Principales

### 1. `display_menu()`
Muestra el menú principal de opciones al usuario.

### 2. `option_1()`
Configura una onda arbitraria solicitando frecuencia, ciclos y amplitud al usuario.

### 3. `option_2()`
Consulta el estado del modo ráfaga (burst) del generador.

### 4. `option_3()`
Configura una señal sinusoidal (frecuencia, amplitud, offset).

### 5. `option_4()`
Activa o desactiva el modo burst y permite configurar el número de ciclos.

### 6. `option_5()`
Consulta y muestra el estado del canal 1 del generador.

### 7. `option_6()`
Enciende el generador de funciones.

### 8. `option_7()`
Apaga el generador de funciones.

### 9. `option_8()` y `option_9()`
Opciones no implementadas aún.

### 10. `main()`
Función principal que ejecuta el menú de opciones y maneja la interacción del usuario.

## Requisitos

- Python 3.x
- Librería `time` para pausas en la ejecución.
- Un módulo llamado `generator_functions` que contenga las funciones específicas para controlar el generador Rigol DG1022.

## Uso

1. Asegúrate de que el generador de funciones Rigol DG1022 esté correctamente conectado.
2. Ejecuta el script de Python. El menú aparecerá en la consola.
3. Selecciona una opción ingresando el número correspondiente.

```python
python menu.py
