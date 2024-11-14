# Valores posibles para los sliders
VALORES_RANGO = [200, 500, 1000, 2000, 5000]

def obtener_valor_slider(slider):
    """Obtiene el valor mapeado del slider a partir de VALORES_RANGO."""
    indice = slider.value()  # Usamos el valor del slider como índice
    return VALORES_RANGO[indice]

def rango_ch1_set(slider):
    """Imprime el valor del slider de Rango Canal 1."""
    valor = obtener_valor_slider(slider)
    print(f"Valor del Rango Canal 1: {valor}")

def rango_ch2_set(slider):
    """Imprime el valor del slider de Rango Canal 2."""
    valor = obtener_valor_slider(slider)
    print(f"Valor del Rango Canal 2: {valor}")

def aplicar_cambios(slider_ch1, slider_ch2, slider_muestras):
    """Imprime todos los valores de los sliders (Rango Canal 1, Rango Canal 2 y Muestras)."""
    valor_ch1 = obtener_valor_slider(slider_ch1)
    valor_ch2 = obtener_valor_slider(slider_ch2)
    valor_muestras = slider_muestras.value()

    print(f"Aplicar Cambios - Valores actuales:\n"
          f"Rango Canal 1: {valor_ch1}\n"
          f"Rango Canal 2: {valor_ch2}\n"
          f"Muestras: {valor_muestras}")

def cargar_configuracion():
    """Imprime un mensaje de carga de configuración."""
    print("Cargando configuración...")

def guardar_configuracion():
    """Imprime un mensaje de guardado de configuración."""
    print("Guardando configuración...")
