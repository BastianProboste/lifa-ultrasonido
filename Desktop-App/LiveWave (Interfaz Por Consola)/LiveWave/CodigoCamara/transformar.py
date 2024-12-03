import cv2
import os

# Ruta de la carpeta donde están las imágenes
carpeta_imagenes = r'C:\Users\AcuphyLab\Desktop\LiveWave\LiveWave\FotosCamara'  # Cambia esto a la ruta de tu carpeta

# Ruta del archivo de salida donde se guardará la información
archivo_salida = 'resultado.txt'

# Abre el archivo en modo de escritura
with open(archivo_salida, 'w') as f:
    # Recorre todos los archivos en la carpeta
    for archivo in os.listdir(carpeta_imagenes):
        # Verifica si el archivo es una imagen (por ejemplo, con extensiones .jpg, .png)
        if archivo.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            # Obtiene la ruta completa de la imagen
            ruta_imagen = os.path.join(carpeta_imagenes, archivo)

            # Lee la imagen
            imagen = cv2.imread(ruta_imagen)

            if imagen is not None:
                # Convierte la imagen a escala de grises
                imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

                # Calcula el área (número de píxeles)
                area = imagen_gris.size

                # Guarda el nombre de la imagen y su área en el archivo de salida
                f.write(f'Imagen: {archivo}, Área: {area} píxeles\n')

                # Guarda la imagen en escala de grises en un archivo nuevo (opcional)
                nombre_imagen_gris = os.path.splitext(archivo)[0] + '_gris' + os.path.splitext(archivo)[1]
                ruta_imagen_gris = os.path.join(carpeta_imagenes, nombre_imagen_gris)
                cv2.imwrite(ruta_imagen_gris, imagen_gris)

print(f'Proceso completado. Los resultados se guardaron en {archivo_salida}')
