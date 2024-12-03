# -*- coding: utf-8 -*-
"""
Convierte datos de deformación en voltios a milímetros desde un archivo existente (sin requerir encabezado).
"""

import os

# Solicitar archivo de entrada y validar existencia
input_file = input("Introduce el nombre del archivo de entrada (incluye .txt): ")
if not os.path.exists(input_file):
    print(f"El archivo '{input_file}' no existe. Verifica el nombre e inténtalo de nuevo.")
    exit(1)

# Solicitar el factor de conversión
try:
    factor_conversion = float(input("Introduce el factor de conversión (mm/V): "))
except ValueError:
    print("Por favor, ingresa un número válido.")
    exit(1)

# Nombre del archivo de salida
output_file = f"deformacion_mm_{os.path.splitext(input_file)[0]}.txt"

# Procesar el archivo
try:
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        # Leer datos y procesarlos
        for line_number, line in enumerate(infile):
            line = line.strip()
            if not line:
                continue  # Saltar líneas vacías
            
            # Dividir línea por comas (formato CSV esperado)
            columns = line.split(",")
            if len(columns) < 2:
                print(f"Línea mal formateada en la línea {line_number + 1}: {line}")
                continue
            
            # Obtener amplitud (en voltios)
            try:
                amplitude = float(columns[1])  # Se asume que la amplitud está en la segunda columna
            except ValueError:
                print(f"Amplitud no válida en la línea {line_number + 1}: {line}")
                continue
            
            # Convertir a milímetros
            deformation_mm = amplitude * factor_conversion

            # Si es la primera línea, agregar encabezado al archivo de salida
            if line_number == 0:
                outfile.write(f"Tiempo,Amplitud (V),Deformacion (mm)\n")
            
            # Escribir la línea con la nueva columna en el archivo de salida
            outfile.write(f"{line},{deformation_mm:.3f}\n")
    
    print(f"Conversión completada. Archivo guardado como: {output_file}")

except Exception as e:
    print(f"Error al procesar el archivo: {e}")
