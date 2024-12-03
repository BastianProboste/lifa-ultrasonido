# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 11:15:29 2021

@author: alejandro
"""

import pyvisa
import time 
import matplotlib.pyplot as plt
import numpy as np

class dg1022:
    def __init__(self):
        self.handle = pyvisa.ResourceManager()
        self.name_list = self.handle.list_resources()
        self.name = ''
        self.inst = None
        self.connected = False
    def conect(self,index):
        try:
            self.name = self.name_list[index]
            self.inst = self.handle.open_resource(self.name)
            self.connected = True
            print(self.name_list)
        except Exception as e:
            print("Unable to connect error %s: "%str(e))
            self.connected = False
    def read(self): 
        try: 
            response = self.inst.read() 
            return response 
        except Exception as e: 
            print(f"Error reading response: {str(e)}")  
            return None
    def query(self, msg):
        try:
            response = self.inst.query(msg)
            print(f"Query: {msg}, Response: {response}")
            return response
        except Exception as e:
            print(f"Error querying message {msg}: {str(e)}")
            return None
    def write(self,msg):
        resp = self.inst.write(msg)
        time.sleep(0.1)

        # comparar largo de mensaje con numeros de bytes recibidos
    def custom_signal(self,signal, plot = False, low = 0 , high =16383, v_max = 1.0, v_min = -1.0):
        # convierte una cadena de puntos en una señal, signal debe ser un objeto iterable
        # esta señal queda guardada en la memoria volatil del generador
        cur_high, cur_low = max(signal),min(signal)
        print(cur_high, cur_low)
        signal = [int((high-low)*(val-cur_low)/(cur_high-cur_low)+low) for val in signal]
        if plot == True:
            plt.plot(signal)
        signal = ''.join([str(d)+',' for d in signal])
        self.write("VOLT:UNIT VPP")
        self.write("VOLT:HIGH "+str(v_max))
        self.write("VOLTage:LOW "+str(v_min))
        self.write("DATA:DEL")
        self.write("DATA:DAC VOLATILE,"+signal[:-1])
        time.sleep(0.5)
    def use_custom_signal(self):
        self.write("FUNC:USER VOLATILE")
        self.write("OUTP ON")
    def gauss(self,frec,n,amp):
        t = np.linspace(0,1,100)
        y = np.exp(-((t-0.5)/0.5)**2)*np.sin(n*2*np.pi*t)
        print(max(y))
        self.custom_signal(signal = y, v_max = amp, v_min = -amp)
        self.write("FREQ "+str(int(frec/n)))
        time.sleep(0.2)        
        print("FREQ "+str(int(frec/n)))
####ELIMINAR DESDE AQUI HASTA ABAJO ####
controller = dg1022()
controller.conect(0)
controller.write('*IDN?')
print(controller.read())