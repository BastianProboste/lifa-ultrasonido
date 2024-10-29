import pyvisa

import time

class Generadorfunciones:
    def __init__(self):
        self.rm = pyvisa.ResourceManager() # Instancia de PYVISA, Gestor de comunicaciones con los dispositivos
        self.instrument = None # Objeto que representa la coneccion activa con el generador de funciones
    #############################################################################################################################
    # Este metodo listara los recursos deisponibles por PYVISA, los recorre y espera que alguno de                              #
    # Se identifique como el generarador de funcion RIGOL DG1022                                                                #
    # Si no es el generador especificado, cierra la conexion pyvisa retorna FALSE eh imprime por consola Que no se encontro     #
    # Si salta algun error en en este flujo, imprime el error por consola y no se interrumpe el codigo.                         #
    #############################################################################################################################

    def connect(self):
        try:
            # Busca el dispositivo conectado por USB
            resources = self.rm.list_resources()
            for resource in resources:
                if 'USB' in resource:
                    # Abre el recurso
                    instrument = self.rm.open_resource(resource)
                    
                    # Verifica la identificación del dispositivo
                    idn_response = instrument.query('*IDN?')
                    if 'RIGOL' in idn_response and 'DG1022' in idn_response:
                        self.instrument = instrument
                        print(f"Conectado a {resource} ({idn_response.strip()})")
                        return True
                    else:
                        # Si no es el dispositivo correcto, cierra la conexión
                        instrument.close()

            print("No se encontró un generador de funciones RIGOL DG1022 conectado por USB.")
            return False
        except Exception as e:
            print(f"Error al conectar: {e}")
            return False
    
    # Si hay una conexion activa del generador de funciones, la cierra
    # Ademas vacia el objeto que representa a al conexion con el generador de funciones 
    def disconnect(self):
        if self.instrument:
            self.instrument.close()
            self.instrument = None
            print("Generador desconectado.")
    
    # Retorna TRUE si hay una conexion activa con el generador de funciones en caso contrario retorna FALSE
    def is_connected(self):
        return self.instrument is not None
    
    # Si esta conectado, Manda señal de encendido al generador de funciones
    # Si salta algun error en este proceso, imprime por consola el error y maneja una desconeccion segura
    def turn_on(self):
        if self.is_connected():
            try:
                self.instrument.write("OUTP ON")
                print("Generador encendido.")

            except Exception as e:
                print(f"Error al encender el generador: {e}")
                self.handle_disconnection()
                

    
    # Configura el canal 2 con una onda SINOUDAL con los parámetros especificados
    # Offset, es opcional, es para hacer que la funcion ocile entre estos valores en voltaje      
    # Frecuencia en Hz; Amplitud en Voltaje pico a pico (Vpp); Offset en Voltaje      
    def channel_2(self, frecuencia, amplitud, offset=0):
        if self.is_connected():
            try:
                command = f"APPL:SIN:CH2 {frecuencia},{amplitud},{offset}"
                self.instrument.write(command)
                print(f"Onda sinusoidal en CH2 configurada: {frecuencia} Hz, {amplitud} Vpp, Offset {offset} V.")
            except Exception as e:
                print(f"Error al configurar CH2: {e}")
                self.handle_disconnection()
    
    # Lee el estado del canal 2 y devuelve la configuración actual del canal
    # La salida esperada es del tipo : "SIN,1.000000e+03,5.000000e+00,-1.500000e+00"
    # Que representa un configuracion de : Frecuencia 1000Hz; Amplitud 5.0Vpp; Offset -1.5 V
    def read_channel_2_state(self):
        if self.is_connected():
            try:
                # Envía el comando de consulta para leer el estado de CH2
                response = self.instrument.query("APPLy:CH2?")
                print(f"Estado del Canal 2: {response}")
                return response
            except Exception as e:
                print(f"Error al leer el estado de CH2: {e}")
                self.handle_disconnection()
        else:
            print("No hay conexión activa con el generador.")
    
    # Configura el canal 1 en modo Burst con una onda sinoudal
    #    Parámetros:
    #    - frecuencia: Frecuencia de la onda sinusoidal en Hz
    #    - amplitud: Amplitud pico a pico de la onda en V
    #    - ciclos: Número de ciclos en el modo Burst
    def channel_1_burst(self, frecuencia, amplitud, ciclos):
        if self.is_connected():
            try:
                # Configura el canal 1 en modo sinusoidal
                self.instrument.write(f"APPL:SIN:CH1 {frecuencia},{amplitud}")

                # Activa el modo Burst en CH1
                self.instrument.write("BURS:STAT ON")  # Habilita el modo Burst
                self.instrument.write("BURS:MODE TRIG")  # Establece el modo de Burst a "Triggered"
                self.instrument.write(f"BURS:NCYC {ciclos}")  # Número de ciclos en Burst
                self.instrument.write("BURS:PHAS 0")  # Configura fase inicial en 0
                self.instrument.write("TRIG:SOUR IMM")  # Configura el disparo como inmediato

                print(f"Canal 1 configurado en modo Burst: {frecuencia} Hz, {amplitud} Vpp, {ciclos} ciclos.")
            except Exception as e:
                print(f"Error al configurar CH1 en modo Burst: {e}")
                self.handle_disconnection()
        else:
            print("No hay conexión activa con el generador.")
    
    # Lee el estado del canal 1 y devuelve la configuración actual del canal
    # la salida esperada es del tipo : "SIN,1.000000e+03,5.000000e+00,0.000000e+00"
    # Que representa wave_type; Frecuencia 1000Hz; Amplitud 5.0Vpp; Offset 0 V
    def read_channel_1_state(self):
        if self.is_connected():
            try:
                # Envía el comando de consulta para leer el estado de CH1
                response = self.instrument.query("APPLy:CH1?")
                print(f"Estado actual del Canal 1: {response}")
            
                return response
                
            except Exception as e:
                print(f"Error al leer el estado de CH1: {e}")
                self.handle_disconnection()
        else:
            print("No hay conexión activa con el generador.")
    
    # Si esta conectado, Manda una señal de APAGADO, Y maneja errores y una desconeccion segura                
    def turn_off(self):
        if self.is_connected():
            try:
                self.instrument.write("OUTP OFF")
                print("Generador apagado.")
            except Exception as e:
                print(f"Error al apagar el generador: {e}")
                self.handle_disconnection()
    
    # Este metodo cierra la coneccion de pyvisa con el generador de funciones de manera correcta e intenta reconectar una sola vez
    def handle_disconnection(self):
        print("Desconexión detectada. Intentando reconectar...")
        self.disconnect()
        time.sleep(1)  # Espera un momento antes de intentar reconectar
        if self.connect():
            print("Reconectado exitosamente.")
            return True
        else:
            print("No se pudo reconectar.")
            return False
    
    # Si hay una conexion activa con el generador de funciones la cierra, y luego cierra la intancia de PYVISA
    def close(self):
        self.disconnect()
        self.rm.close()

if __name__ == "__main__":
    controller = Generadorfunciones()
    if controller.connect():
        try:
            controller.turn_on()
            time.sleep(2)  # Espera 2 segundos
            controller.turn_off()
        except KeyboardInterrupt:
            print("Interrupción del usuario.")
        finally:
            controller.close()

## IMPORTANTE, NOTA:
# Falta validar el rango de los parametros para la funciones que configuran los canales