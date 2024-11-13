# lifa-ultrasonido
## Descripcion
Este proyecto tiene como objetivo cuantificar cambios microestructurales en muestras de acero sometidas a tracción mediante ultrasonido. Utiliza un generador de funciones, transductores, una máquina de tracción, una cámara, y un sensor inductivo para medir parámetros físicos durante la deformación.

Además, se emplea un Arduino para medir la deformación directa con un sensor strain gauge. Los datos se procesan en un PC principal, mientras otro PC monitoriza el ensayo en tiempo real. La metodología Scrum organiza el trabajo en sprints semanales para asegurar entregas continuas y funcionales.

## Indice

## 📂 Instalación

Para instalar y ejecutar el proyecto `lifa-ultrasonido`, sigue estos pasos:

### 1. Clonar el repositorio

Clona el repositorio a tu máquina local utilizando Git:
```bash
git clone https://github.com/BastianProboste/lifa-ultrasonido.git
```
### 2. Crear un entorno en conda
Para crear un entorno en conda es de esta manera:

![image](https://github.com/user-attachments/assets/cf8c89ee-c585-4e1b-8158-7343f917c6e4)

Luego de creara el entorno installar los requeriments.txt de esta manera:

![image](https://github.com/user-attachments/assets/ce1376c4-912c-44cc-97f8-099d5ec2d85b)

De esta misma manera se instala requirements2.txt



## Requerimientos
Software, bibliotecas o entornos necesarios para que funcione el proyecto (ejemplo: versiones de Python, Node.js, etc.).


## Soporte visual
![image](https://github.com/user-attachments/assets/49f36865-22c3-4e3b-887f-6b430802f2d1)
Esta imagen representa el login de la pagina web del proyecto, en la caul estara un modulo de ensayo y un modulo de gestion de usuarios en donde se podran crear, editar  y eliminar usuarios. Las siguientes imagenes corresponderan a lo antes mencionado

### Modulo de gestion usuario
![image](https://github.com/user-attachments/assets/7aa8b83b-52c5-4c84-9cec-9dde561955a7)

![image](https://github.com/user-attachments/assets/669e6ad6-585b-438d-80bf-a672f9f392b9)

### Modulo de ensayo



### Interfaz GUI
Estas imagen corresponderan al diseño de la interfaz GUI la cual se abrira desde el sescritorio del computador del laboratorio.

### Ensayo
![image](https://github.com/user-attachments/assets/c3a5044a-c906-4a1c-8554-0c79e4fa49ff)
La imagen que se observa es la pagina de ensayo de la interfaz la cual iran todos los datos neciesarios para iniciar el ensayo y los datos que se obtendran mediante la camara.

### Cargar datos
![Imagen de WhatsApp 2024-11-07 a las 13 00 59_e11bb7fe](https://github.com/user-attachments/assets/ee667aef-d051-438a-854d-8401ba783738)

En esta ventana de la interfaz verificaremos que se esten detectando los equipos para luego conectarlos, tambien se añadira los datos para el generdador de funciones y darle al boton guardar para que esta configuracion quede almacenada en la base de datos.



### Equipos
PC1:
Este es el ordenador principal encargado de controlar y configurar los elementos del ensayo de tracción. A través de este equipo, se gestionan los datos provenientes de los sensores, la tarjeta de adquisición Phidget, el generador de funciones y la cámara. También envía la señal para iniciar la adquisición de datos en el PC2. Esta es la imagen del PC1.

PC2:
Este ordenador recibe y visualiza los datos del ensayo de tracción en tiempo real. Utiliza el software "WDW TEST CONTROL" para monitorear variables clave, como la fuerza aplicada y la deformación de la muestra. Se comunica con el PC1 para iniciar la adquisición de datos. La imagen del PC2.

Generador de funciones (DG1022):
Este dispositivo genera las ondas ultrasónicas que se transmiten a través de la muestra de acero. El generador de funciones permite configurar la amplitud, frecuencia y el número de ciclos de las señales ultrasónicas emitidas, y está conectado al sistema mediante USB para que se le puedan enviar comandos de control desde el PC1.


Máquina de tracción (HD-B612-10S):
La máquina de tracción es la encargada de aplicar la fuerza de tensión a la muestra de acero. Durante el ensayo, esta máquina estira la muestra hasta que se produce una fractura, y los datos de fuerza y desplazamiento se transmiten al sistema para su análisis.

Cámara:
La cámara se utiliza para monitorear el espesor del material durante el ensayo. Ubicada frente a la muestra, captura cambios visuales en el espesor en tiempo real. Esto ayuda a calcular la deformación transversal del material mientras se lleva a cabo el ensayo.

Sensor inductivo:
Este sensor mide el espesor en áreas de la muestra que la cámara no puede captar adecuadamente. Complementa la información proporcionada por la cámara, asegurando una medición precisa del espesor en varios puntos de la muestra.

Phidget:
El Phidget es una tarjeta de adquisición conectada vía USB que recibe las señales del sensor inductivo y del strain gauge. Se usa para capturar datos específicos del ensayo, especialmente relacionados con la fuerza aplicada y el espesor del material.

## Uso
Instrucciones sobre cómo utilizar el proyecto




