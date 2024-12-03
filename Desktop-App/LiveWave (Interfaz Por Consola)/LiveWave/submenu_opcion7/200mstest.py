import time
from datetime import datetime
from GageAcquire4 import SistemaGage, ConfiguradorGage, AdquisidorGage, ConvertidorVoltajes, GuardadorDatos


# =============================================================================
# Función de disparo para probar el sistema Gage
# =============================================================================
def disparar_funcion(adquisidor, convertidor, guardador, contador):
    """
    Función que dispara la adquisición de datos utilizando el sistema Gage.

    Parámetros:
    - adquisidor: Instancia de la clase AdquisidorGage.
    - convertidor: Instancia de la clase ConvertidorVoltajes.
    - guardador: Instancia de la clase GuardadorDatos.
    - contador: Contador para diferenciar archivos guardados.
    """
    try:
        # Adquirir datos crudos desde el sistema Gage
        data_ch1, _ = adquisidor.adquirir(0, 2048)
       # data_ch2, _ = adquisidor.adquirir(0, 2048)

        # Convertir los datos a voltajes
        voltajes_ch1 = convertidor.convertir(data_ch1, 2000, 500, 4096, 2048)
      #  voltajes_ch2 = convertidor.convertir(data_ch2, 2000, 500, 4096, 2048)


        # Guardar los datos adquiridos en un archivo
        filename = f"test_200ms_ch1_{contador}.txt"
        guardador.guardar(filename, voltajes_ch1)

       # filename = f"test_200ms_ch2_{contador}.txt"
       # guardador.guardar(filename, voltajes_ch2)
       # print(f"Datos guardados en {filename}")

    except RuntimeError as e:
        print(f"Error durante la adquisición: {e}")


# =============================================================================
# Log para validar tiempos de ejecución
# =============================================================================
def registrar_log(log_file, tiempo_requerido, tiempo_real):
    """
    Registra los tiempos reales de ejecución en un archivo de log.

    Parámetros:
    - log_file: Archivo de log donde se escribirán los registros.
    - tiempo_requerido: Tiempo esperado entre ejecuciones (en ms).
    - tiempo_real: Tiempo real entre ejecuciones (en ms).
    """
    with open(log_file, "a") as file:
        file.write(f"Tiempo requerido: {tiempo_requerido}ms | Tiempo real: {tiempo_real:.2f}ms\n")


# =============================================================================
# Script principal
# =============================================================================
def main():
    log_file = "200ms_test_log.txt"
    tiempo_requerido = 200  # Tiempo requerido en milisegundos
    tiempo_requerido_s = tiempo_requerido / 1000  # Convertir a segundos

    print(f"Iniciando prueba de disparos cada {tiempo_requerido}ms...")
    print(f"Log guardado en: {log_file}")

    # Limpiar el archivo de log anterior
    with open(log_file, "w") as file:
        file.write(f"Log de prueba 200ms iniciado: {datetime.now()}\n")
        file.write("=" * 50 + "\n")

    # Inicializar el sistema Gage
    sistema = SistemaGage()
    try:
        sistema.inicializar()
        configurador = ConfiguradorGage(sistema.handle)
        configurador.configurar()
        adquisidor = AdquisidorGage(sistema.handle)
        convertidor = ConvertidorVoltajes()
        guardador = GuardadorDatos()

        tiempo_anterior = time.time()
        contador = 0

        # Ciclo principal de prueba
        while True:
            tiempo_actual = time.time()
            tiempo_real = (tiempo_actual - tiempo_anterior) * 1000  # Tiempo real en ms

            # Validar si ha pasado el tiempo requerido
            if tiempo_real >= tiempo_requerido:
                # Disparar adquisición con el sistema Gage
                disparar_funcion(adquisidor, convertidor, guardador, contador)

                # Registrar el tiempo real en el log
                registrar_log(log_file, tiempo_requerido, tiempo_real)

                # Actualizar el tiempo anterior y el contador
                tiempo_anterior = tiempo_actual
                contador += 1

            # Pequeña pausa para no saturar la CPU
            time.sleep(0.001)

    except KeyboardInterrupt:
        print("Prueba interrumpida por el usuario.")

    finally:
        sistema.liberar()


if __name__ == "__main__":
    main()
