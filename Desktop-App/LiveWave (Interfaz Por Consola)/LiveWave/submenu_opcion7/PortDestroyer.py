import psutil
import os

def liberar_puertos_com():
    print("Buscando procesos que usan puertos COM...")

    # Lista de posibles nombres asociados a programas que abren puertos COM
    posibles_programas = ["python", "putty", "serial", "arduino", "com"]

    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            nombre = proc.info['name'].lower()
            pid = proc.info['pid']

            # Si el nombre del proceso está relacionado con puertos COM
            if any(prog in nombre for prog in posibles_programas):
                print(f"Encontrado: {nombre} (PID: {pid}). Intentando cerrar...")
  #              os.kill(pid, 9)  # Forzar la terminación del proceso
  #              print(f"Proceso {nombre} (PID: {pid}) cerrado con éxito.")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"No se pudo cerrar un proceso: {e}")

    print("Finalizado. Los puertos COM deberían estar libres.")

if __name__ == "__main__":
    liberar_puertos_com()
