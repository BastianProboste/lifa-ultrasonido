# funciones_ensayo.py

import random

def maquina_traccion_visual(lcd_tiempo, lcd_desplazamiento, lcd_fuerza):
    """Actualiza los valores de tiempo, desplazamiento y fuerza en los LCD."""
    # Valores simulados
    tiempo_valor = round(random.uniform(10.0, 20.0), 2)  # Simulación de un valor entre 10.0 y 20.0
    desplazamiento_valor = round(random.uniform(50.0, 100.0), 2)  # Entre 50.0 y 100.0
    fuerza_valor = round(random.uniform(80.0, 120.0), 2)  # Entre 80.0 y 120.0

    # Actualizar los valores en los LCD
    lcd_tiempo.display(tiempo_valor)
    lcd_desplazamiento.display(desplazamiento_valor)
    lcd_fuerza.display(fuerza_valor)

def imprimir_material_elegido(combo_box):
    """Imprime en consola el material elegido en el ComboBox."""
    material_seleccionado = combo_box.currentText()
    print(f"Material seleccionado: {material_seleccionado}")

def iniciar_ensayo(combo_material, line_gf, line_resistencia, line_voltaje, line_ancho, line_espesor):
    """Imprime en consola los valores seleccionados y configurados para iniciar el ensayo."""
    material_seleccionado = combo_material.currentText()
    gf = line_gf.text()
    resistencia = line_resistencia.text()
    voltaje = line_voltaje.text()
    ancho = line_ancho.text()
    espesor = line_espesor.text()

    print("Iniciando ensayo con los siguientes valores:")
    print(f"Material: {material_seleccionado}")
    print(f"GF: {gf}")
    print(f"Resistencia: {resistencia}")
    print(f"Voltaje: {voltaje}")
    print(f"Ancho: {ancho}")
    print(f"Espesor: {espesor}")
