# -*- coding: utf-8 -*-
# Este archivo define la estructura principal de la ventana de la aplicación.
import funciones_cargar_datos
from funciones_ensayo import *
from funciones_generador import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        """ Inicializa la ventana principal con tamaño fijo, barra de menú, barra de estado y pestañas principales """
        super(MainWindow, self).__init__()

        # Configuración de ventana
        self.setGeometry(QtCore.QRect(0, 0, 1068, 700))
        self.setMinimumSize(QtCore.QSize(1068, 700))
        self.setMaximumSize(QtCore.QSize(1068, 700))
        self.setWindowTitle("MainWindow")

        # Widget central
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Configuración de la barra de menú y acciones
        self._configurar_menu()

        # Barra de estado
        self.status_bar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Configuración de pestañas principales
        self._configurar_tabs()

    def _configurar_menu(self):
        """ Configura la barra de menu principal y sus opciones """

        # Crear la barra de menu
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 1068, 18))

        # Seccion del menu principal: LiFa Wave APP
        self.menu_lifa_wave_app = QtWidgets.QMenu("LiFa Wave APP", self.menu_bar)
        self.menu_lifa_wave_app.setEnabled(False)  # Menu deshabilitado

        # Accion: Seleccionar Idioma
        self.action_seleccionar_idioma = QtWidgets.QAction("Seleccionar Idioma", self)
        self.menu_lifa_wave_app.addAction(self.action_seleccionar_idioma)  # Anadir accion al menu principal

        # Anadir el menu principal a la barra de menu
        self.menu_bar.addAction(self.menu_lifa_wave_app.menuAction())
        self.setMenuBar(self.menu_bar)

    def _configurar_tabs(self):
        """ Configura las pestañas principales: 'Cargar Datos', 'Ensayo' y 'Generador de Funciones' """

        # Tab Widget
        self.tab_widget = QtWidgets.QTabWidget(self.central_widget)
        self.main_layout.addWidget(self.tab_widget)

        # Tab Cargar Datos
        self.tab_cargar_datos = QtWidgets.QWidget()
        self._configurar_tab_cargar_datos()
        self.tab_widget.addTab(self.tab_cargar_datos, "Cargar Datos")

        # Tab Ensayo
        self.tab_ensayo = QtWidgets.QWidget()
        self._configurar_tab_ensayo()
        self.tab_widget.addTab(self.tab_ensayo, "Ensayo")

        # Tab Generador de Funciones
        self.tab_generador_funciones = QtWidgets.QWidget()
        self._configurar_tab_generador_funciones()
        self.tab_widget.addTab(self.tab_generador_funciones, "Generador de Funciones")

    def _configurar_tab_cargar_datos(self):
        """ Configura la pestaña 'Cargar Datos' con todos sus elementos y widgets """

        # Crear layout principal de la pestaña
        self.tab_cargar_datos = QtWidgets.QWidget()
        layout_principal = QtWidgets.QVBoxLayout(self.tab_cargar_datos)

        # **Sección Generador de Funciones**
        box_generador_funciones = QtWidgets.QGroupBox("Generador de Funciones")
        box_generador_funciones.setGeometry(10, 330, 600, 100)
        layout_generador_funciones = QtWidgets.QHBoxLayout(box_generador_funciones)

        # Botón Cargar
        self.btn_cargar_generador = QtWidgets.QPushButton("Cargar")
        self.btn_cargar_generador.setMinimumSize(180, 50)
        layout_generador_funciones.addWidget(self.btn_cargar_generador)
        self.btn_cargar_generador.clicked.connect(funciones_cargar_datos.cargar_generador_funciones)  # Conectar con función

        # ComboBox Generador de Funciones
        self.combo_generador_funciones = QtWidgets.QComboBox()
        self.combo_generador_funciones.setMinimumSize(180, 50)
        layout_generador_funciones.addWidget(self.combo_generador_funciones)

        # Botón Conectar
        self.btn_conectar_generador = QtWidgets.QPushButton("Conectar")
        self.btn_conectar_generador.setMinimumSize(180, 50)
        layout_generador_funciones.addWidget(self.btn_conectar_generador)
        self.btn_conectar_generador.clicked.connect(funciones_cargar_datos.conectar_generador_funciones)  # Conectar con función

        layout_principal.addWidget(box_generador_funciones)

        # **Sección Cámara**
        box_camara = QtWidgets.QGroupBox("Cámara")
        box_camara.setGeometry(10, 420, 600, 100)
        layout_camara = QtWidgets.QHBoxLayout(box_camara)

        # Botón Conectar
        self.btn_conectar_camara = QtWidgets.QPushButton("Conectar")
        self.btn_conectar_camara.setMinimumSize(100, 50)
        layout_camara.addWidget(self.btn_conectar_camara)
        self.btn_conectar_camara.clicked.connect(funciones_cargar_datos.conectar_camara)  # Conectar con función

        # Botón Test
        self.btn_test_camara = QtWidgets.QPushButton("Test")
        self.btn_test_camara.setMinimumSize(100, 50)
        layout_camara.addWidget(self.btn_test_camara)
        self.btn_test_camara.clicked.connect(funciones_cargar_datos.test_camara)  # Conectar con función

        layout_principal.addWidget(box_camara)

        # **Sección Máquina de Tracción**
        box_maquina_traccion = QtWidgets.QGroupBox("Máquina de Tracción")
        box_maquina_traccion.setGeometry(10, 510, 600, 100)
        layout_maquina_traccion = QtWidgets.QHBoxLayout(box_maquina_traccion)

        # Botón Cargar
        self.btn_cargar_maquina = QtWidgets.QPushButton("Cargar")
        self.btn_cargar_maquina.setMinimumSize(180, 50)
        layout_maquina_traccion.addWidget(self.btn_cargar_maquina)
        self.btn_cargar_maquina.clicked.connect(funciones_cargar_datos.cargar_maquina_traccion)  # Conectar con función

        # ComboBox Máquina de Tracción
        self.combo_maquina_traccion = QtWidgets.QComboBox()
        self.combo_maquina_traccion.setMinimumSize(180, 50)
        layout_maquina_traccion.addWidget(self.combo_maquina_traccion)

        # Botón Conectar
        self.btn_conectar_maquina = QtWidgets.QPushButton("Conectar")
        self.btn_conectar_maquina.setMinimumSize(180, 50)
        layout_maquina_traccion.addWidget(self.btn_conectar_maquina)
        self.btn_conectar_maquina.clicked.connect(funciones_cargar_datos.conectar_maquina_traccion)  # Conectar con función

        layout_principal.addWidget(box_maquina_traccion)

        # **Sección Generador de Captura de Datos**
        layout_generador_captura = QtWidgets.QHBoxLayout()

        # Generador de Funciones
        box_generador_funciones_grande = QtWidgets.QGroupBox("Generador de Funciones")
        layout_generador_grande = QtWidgets.QGridLayout(box_generador_funciones_grande)

        # Etiqueta y entrada de Amplitud
        self.lbl_amplitud = QtWidgets.QLabel("Amplitud:")
        layout_generador_grande.addWidget(self.lbl_amplitud, 0, 0)
        self.line_amplitud = QtWidgets.QLineEdit()
        layout_generador_grande.addWidget(self.line_amplitud, 0, 1)

        # Etiqueta y entrada de Frecuencia
        self.lbl_frecuencia = QtWidgets.QLabel("Frecuencia:")
        layout_generador_grande.addWidget(self.lbl_frecuencia, 1, 0)
        self.line_frecuencia = QtWidgets.QLineEdit()
        layout_generador_grande.addWidget(self.line_frecuencia, 1, 1)

        # Etiqueta y entrada de N° de Ciclos
        self.lbl_numero_ciclos = QtWidgets.QLabel("N° de Ciclos:")
        layout_generador_grande.addWidget(self.lbl_numero_ciclos, 2, 0)
        self.line_numero_ciclos = QtWidgets.QLineEdit()
        layout_generador_grande.addWidget(self.line_numero_ciclos, 2, 1)

        # Botón Guardar
        self.btn_guardar_generador = QtWidgets.QPushButton("Guardar")
        layout_generador_grande.addWidget(self.btn_guardar_generador, 3, 0, 1, 2)
        self.btn_guardar_generador.clicked.connect(funciones_cargar_datos.guardar_generador_funciones)  # Conectar con función

        layout_generador_captura.addWidget(box_generador_funciones_grande)

        # Captura de Datos
        box_captura_datos = QtWidgets.QGroupBox("Captura de Datos")
        layout_captura_datos = QtWidgets.QGridLayout(box_captura_datos)

        # Etiqueta y entrada de Escala
        self.lbl_escala = QtWidgets.QLabel("Escala:")
        layout_captura_datos.addWidget(self.lbl_escala, 2, 0)
        self.line_escala = QtWidgets.QLineEdit()
        layout_captura_datos.addWidget(self.line_escala, 2, 1)

        # Etiqueta y entrada de N° de Muestras
        self.lbl_numero_muestras = QtWidgets.QLabel("N° de Muestras:")
        layout_captura_datos.addWidget(self.lbl_numero_muestras, 3, 0)
        self.line_numero_muestras = QtWidgets.QLineEdit()
        layout_captura_datos.addWidget(self.line_numero_muestras, 3, 1)

        # Etiqueta y entrada de Frecuencia de Muestreo
        self.lbl_frecuencia_muestreo = QtWidgets.QLabel("Frecuencia de Muestreo:")
        layout_captura_datos.addWidget(self.lbl_frecuencia_muestreo, 0, 0)
        self.line_frecuencia_muestreo = QtWidgets.QLineEdit()
        layout_captura_datos.addWidget(self.line_frecuencia_muestreo, 0, 1)

        # Etiqueta y entrada de N° de Canales
        self.lbl_numero_canales = QtWidgets.QLabel("N° de Canales:")
        layout_captura_datos.addWidget(self.lbl_numero_canales, 1, 0)
        self.line_numero_canales = QtWidgets.QLineEdit()
        layout_captura_datos.addWidget(self.line_numero_canales, 1, 1)

        layout_generador_captura.addWidget(box_captura_datos)
        layout_principal.addLayout(layout_generador_captura)

        # **Sección Test Cámara**
        self.test_camara_frame = QtWidgets.QFrame()
        self.test_camara_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.test_camara_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        layout_principal.addWidget(self.test_camara_frame)

        # Establecer el layout de la pestaña
        self.tab_cargar_datos.setLayout(layout_principal)

    def cargar_archivo_funciones(self): #NO TIENE USO AUN
        """
        Abre un cuadro de diálogo para seleccionar un archivo y agrega el nombre del archivo seleccionado
        al QComboBox correspondiente a la sección "Generador de Funciones".
        """
        opciones = QFileDialog.Options()
        opciones |= QFileDialog.ReadOnly

        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "",
                                                 "Archivos de Datos (*.csv *.txt);;Todos los Archivos (*)",
                                                 options=opciones)

        if archivo:
            nombre_archivo = archivo.split("/")[-1]
            self.cmb_seleccion_funciones.addItem(nombre_archivo)

    def _configurar_tab_ensayo(self):
        """Configura la pestaña 'Ensayo' con todos sus elementos y widgets"""

        # Crear layout principal de la pestaña Ensayo
        self.tab_ensayo = QtWidgets.QWidget()
        layout_principal = QtWidgets.QHBoxLayout(self.tab_ensayo)

        # **Sección Máquina de Tracción**
        maquina_traccion_layout = QtWidgets.QVBoxLayout()
        self.lbl_maquina_traccion = QtWidgets.QLabel("Maquina de tracción")
        self.lbl_maquina_traccion.setMinimumSize(200, 100)
        self.lbl_maquina_traccion.setMaximumSize(200, 100)
        self.lbl_maquina_traccion.setStyleSheet("color: rgb(255, 255, 255); font: 16pt 'MS Shell Dlg 2';")
        maquina_traccion_layout.addWidget(self.lbl_maquina_traccion)

        # Layout para los LCDs de Tiempo, Desplazamiento y Fuerza
        tiempo_desplazamiento_fuerza_layout = QtWidgets.QGridLayout()

        # LCD para Tiempo
        self.lbl_tiempo = QtWidgets.QLabel("Tiempo")
        self.lbl_tiempo.setMinimumSize(120, 50)
        self.lbl_tiempo.setStyleSheet("background-color: rgb(165, 202, 234); font: 14pt Consolas; color: #000000;")
        tiempo_desplazamiento_fuerza_layout.addWidget(self.lbl_tiempo, 2, 0)
        self.lcd_tiempo = QtWidgets.QLCDNumber()
        tiempo_desplazamiento_fuerza_layout.addWidget(self.lcd_tiempo, 3, 0)

        # LCD para Desplazamiento
        self.lbl_desplazamiento = QtWidgets.QLabel("Desplazamiento")
        self.lbl_desplazamiento.setMinimumSize(120, 50)
        self.lbl_desplazamiento.setStyleSheet(
            "background-color: rgb(165, 202, 234); font: 14pt Consolas; color: #000000;")
        tiempo_desplazamiento_fuerza_layout.addWidget(self.lbl_desplazamiento, 2, 1)
        self.lcd_desplazamiento = QtWidgets.QLCDNumber()
        tiempo_desplazamiento_fuerza_layout.addWidget(self.lcd_desplazamiento, 3, 1)

        # LCD para Fuerza
        self.lbl_fuerza = QtWidgets.QLabel("Fuerza")
        self.lbl_fuerza.setMinimumSize(120, 50)
        self.lbl_fuerza.setStyleSheet("background-color: rgb(165, 202, 234); font: 14pt Consolas; color: #000000;")
        tiempo_desplazamiento_fuerza_layout.addWidget(self.lbl_fuerza, 2, 2)
        self.lcd_fuerza = QtWidgets.QLCDNumber()
        tiempo_desplazamiento_fuerza_layout.addWidget(self.lcd_fuerza, 3, 2)

        # Configuración del QTimer para actualizar LCD cada 200ms
        self.timer = QTimer()
        self.timer.timeout.connect(
            lambda: maquina_traccion_visual(self.lcd_tiempo, self.lcd_desplazamiento, self.lcd_fuerza))
        self.timer.start(200)  # Actualización cada 200ms



        maquina_traccion_layout.addLayout(tiempo_desplazamiento_fuerza_layout)

        # Layout para Material y Tiempo Entre Datos
        material_layout = QtWidgets.QGridLayout()
        self.lbl_material = QtWidgets.QLabel("Material:")
        self.lbl_material.setMinimumSize(210, 70)
        self.lbl_material.setStyleSheet("background-color: rgb(165, 202, 234); font: 20pt Consolas; color: #000000;")
        material_layout.addWidget(self.lbl_material, 0, 0)
        self.cmb_material_opciones = QtWidgets.QComboBox()
        self.cmb_material_opciones.addItems(["Opciones", "Metal"])
        material_layout.addWidget(self.cmb_material_opciones, 0, 1)

        # ComboBox para elegir Material
        self.cmb_material_opciones = QtWidgets.QComboBox()
        self.cmb_material_opciones.addItems(["Opciones", "Metal"])
        material_layout.addWidget(self.cmb_material_opciones, 0, 1)

        # Conectar señal de cambio de índice de ComboBox a la función
        self.cmb_material_opciones.currentIndexChanged.connect(
            lambda: imprimir_material_elegido(self.cmb_material_opciones)
        )

        self.lbl_tiempo_entre_datos = QtWidgets.QLabel("Tiempo Entre Datos:")
        self.lbl_tiempo_entre_datos.setMinimumSize(210, 70)
        self.lbl_tiempo_entre_datos.setStyleSheet(
            "background-color: rgb(165, 202, 234); font: 12pt Consolas; color: #000000;")
        material_layout.addWidget(self.lbl_tiempo_entre_datos, 1, 0)
        self.line_tiempo_entre_datos = QtWidgets.QLineEdit()
        self.line_tiempo_entre_datos.setPlaceholderText("Defina Tiempo entre Datos")
        material_layout.addWidget(self.line_tiempo_entre_datos, 1, 1)

        maquina_traccion_layout.addLayout(material_layout)

        # Layout para GF, Resistencia y Voltaje
        gf_resistencia_voltaje_layout = QtWidgets.QGridLayout()

        # GF
        self.lbl_gf = QtWidgets.QLabel("GF")
        self.lbl_gf.setMinimumSize(120, 50)
        self.lbl_gf.setStyleSheet("background-color: rgb(165, 202, 234); font: 12pt Consolas; color: #000000;")
        gf_resistencia_voltaje_layout.addWidget(self.lbl_gf, 0, 0)
        self.line_gf = QtWidgets.QLineEdit()
        self.line_gf.setPlaceholderText("Ingrese GF")
        gf_resistencia_voltaje_layout.addWidget(self.line_gf, 1, 0)

        # Resistencia
        self.lbl_resistencia = QtWidgets.QLabel("Resistencia")
        self.lbl_resistencia.setMinimumSize(120, 50)
        self.lbl_resistencia.setStyleSheet("background-color: rgb(165, 202, 234); font: 12pt Consolas; color: #000000;")
        gf_resistencia_voltaje_layout.addWidget(self.lbl_resistencia, 0, 1)
        self.line_resistencia = QtWidgets.QLineEdit()
        self.line_resistencia.setPlaceholderText("Ingrese Resistencia")
        gf_resistencia_voltaje_layout.addWidget(self.line_resistencia, 1, 1)

        # Voltaje
        self.lbl_voltaje = QtWidgets.QLabel("Voltaje")
        self.lbl_voltaje.setMinimumSize(120, 50)
        self.lbl_voltaje.setStyleSheet("background-color: rgb(165, 202, 234); font: 12pt Consolas; color: #000000;")
        gf_resistencia_voltaje_layout.addWidget(self.lbl_voltaje, 0, 2)
        self.line_voltaje = QtWidgets.QLineEdit()
        self.line_voltaje.setPlaceholderText("Ingrese Voltaje")
        gf_resistencia_voltaje_layout.addWidget(self.line_voltaje, 1, 2)

        maquina_traccion_layout.addLayout(gf_resistencia_voltaje_layout)

        layout_principal.addLayout(maquina_traccion_layout)

        # **Sección Cámara**
        camara_layout = QtWidgets.QGridLayout()

        # Cámara - Ancho y Espesor
        self.lbl_ancho = QtWidgets.QLabel("Ancho:")
        self.lbl_ancho.setMinimumSize(168, 100)
        self.lbl_ancho.setStyleSheet("background-color: rgb(165, 202, 234); font: 12pt Consolas; color: #000000;")
        camara_layout.addWidget(self.lbl_ancho, 2, 0)
        self.line_ancho = QtWidgets.QLineEdit()
        self.line_ancho.setPlaceholderText("Ancho en Pixeles")
        camara_layout.addWidget(self.line_ancho, 3, 0)

        self.lbl_espesor = QtWidgets.QLabel("Espesor:")
        self.lbl_espesor.setMinimumSize(168, 100)
        self.lbl_espesor.setStyleSheet("background-color: rgb(165, 202, 234); font: 12pt Consolas; color: #000000;")
        camara_layout.addWidget(self.lbl_espesor, 2, 1)
        self.line_espesor = QtWidgets.QLineEdit()
        self.line_espesor.setPlaceholderText("Espesor en Cm")
        camara_layout.addWidget(self.line_espesor, 3, 1)

        # Botón Iniciar
        self.btn_iniciar = QtWidgets.QPushButton("Iniciar")
        self.btn_iniciar.setStyleSheet("background-color: rgb(33, 143, 37); border-radius: 10px;")
        self.btn_iniciar.clicked.connect(
            lambda: iniciar_ensayo(self.cmb_material_opciones, self.line_gf, self.line_resistencia, self.line_voltaje,
                                   self.line_ancho, self.line_espesor)
        )
        camara_layout.addWidget(self.btn_iniciar, 4, 0, 1, 2)

        layout_principal.addLayout(camara_layout)

        # Establecer el layout de la pestaña
        self.tab_ensayo.setLayout(layout_principal)

    def _configurar_tab_generador_funciones(self):
        """Configura la pestaña 'Generador Funciones' con todos sus elementos y widgets"""

        # Crear layout principal de la pestaña
        self.tab_generador_funciones = QtWidgets.QWidget()
        layout_principal = QtWidgets.QGridLayout(self.tab_generador_funciones)

        # **Gráfico de Canales**
        self.vista_grafico_canales = QtWidgets.QGraphicsView()
        self.vista_grafico_canales.setMinimumSize(591, 601)
        layout_principal.addWidget(self.vista_grafico_canales, 0, 0)

        # **Controles de Canal y Configuración**
        controles_layout = QtWidgets.QVBoxLayout()

        # **Rango Canal 1**
        rango_ch1_layout = QtWidgets.QGridLayout()
        self.lbl_rango_ch1 = QtWidgets.QLabel("Rango Canal 1")
        rango_ch1_layout.addWidget(self.lbl_rango_ch1, 0, 0, 1, 2)

        self.slider_rango_ch1 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_rango_ch1.setRange(0, 4)  # Índices de los valores predefinidos [200, 500, 1000, 2000, 5000]
        self.slider_rango_ch1.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        rango_ch1_layout.addWidget(self.slider_rango_ch1, 1, 0)

        self.btn_rango_ch1_set = QtWidgets.QPushButton("Set")
        rango_ch1_layout.addWidget(self.btn_rango_ch1_set, 1, 1)
        controles_layout.addLayout(rango_ch1_layout)

        # **Rango Canal 2**
        rango_ch2_layout = QtWidgets.QGridLayout()
        self.lbl_rango_ch2 = QtWidgets.QLabel("Rango Canal 2")
        rango_ch2_layout.addWidget(self.lbl_rango_ch2, 0, 0, 1, 2)

        self.slider_rango_ch2 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_rango_ch2.setRange(0, 4)  # Índices de los valores predefinidos [200, 500, 1000, 2000, 5000]
        self.slider_rango_ch2.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        rango_ch2_layout.addWidget(self.slider_rango_ch2, 1, 0)

        self.btn_rango_ch2_set = QtWidgets.QPushButton("Set")
        rango_ch2_layout.addWidget(self.btn_rango_ch2_set, 1, 1)
        controles_layout.addLayout(rango_ch2_layout)

        # **Muestras Canal 1**
        muestra_ch1_layout = (
            QtWidgets.QGridLayout())
        self.lbl_muestra_ch1 = (
            QtWidgets.QLabel("Muestras"))
        muestra_ch1_layout.addWidget(self.lbl_muestra_ch1, 0, 0, 1, 2)

        self.slider_muestra_ch1 = (
            QtWidgets.QSlider(QtCore.Qt.Horizontal))
        muestra_ch1_layout.addWidget(self.slider_muestra_ch1, 1, 0)

        self.btn_muestra_ch1_set = (
            QtWidgets.QPushButton("Set"))
        muestra_ch1_layout.addWidget(self.btn_muestra_ch1_set, 1, 1)
        controles_layout.addLayout(muestra_ch1_layout)

        # **Botón Aplicar Cambios**
        self.btn_aplicar_cambios = (
            QtWidgets.QPushButton("Aplicar Cambios"))
        controles_layout.addWidget(self.btn_aplicar_cambios)

        # **Botón Cargar Configuración**
        self.btn_cargar_configuracion = (
            QtWidgets.QPushButton("Cargar Configuracion"))
        controles_layout.addWidget(self.btn_cargar_configuracion)

        # **Botón Guardar Configuración**
        self.btn_guardar_configuracion = (
            QtWidgets.QPushButton("Guardar Configuracion"))
        controles_layout.addWidget(self.btn_guardar_configuracion)

        # Agregar layout de controles al layout principal
        layout_principal.addLayout(controles_layout, 0, 1)

        # Establecer el layout de la pestaña
        self.tab_generador_funciones.setLayout(layout_principal)

        # **Conexiones de los botones y sliders**
        self.btn_rango_ch1_set.clicked.connect(
            lambda: rango_ch1_set(self.slider_rango_ch1))
        self.btn_rango_ch2_set.clicked.connect(
            lambda: rango_ch2_set(self.slider_rango_ch2))
        self.btn_muestra_ch1_set.clicked.connect(
            lambda: print(f"Valor del slider Muestras: "
                          f"{self.slider_muestra_ch1.value()}"))

        self.btn_aplicar_cambios.clicked.connect(
            lambda: aplicar_cambios(self.slider_rango_ch1,
                                    self.slider_rango_ch2,
                                    self.slider_muestra_ch1)
        )

        self.btn_cargar_configuracion.clicked.connect(cargar_configuracion)
        self.btn_guardar_configuracion.clicked.connect(guardar_configuracion)


# Ejecución de la aplicación
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec_())
