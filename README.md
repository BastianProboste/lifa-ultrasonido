# lifa-ultrasonido
## Descripcion
Este proyecto tiene como objetivo cuantificar cambios microestructurales en muestras de acero sometidas a tracción mediante ultrasonido. Utiliza un generador de funciones, transductores, una máquina de tracción y  una cámara, para medir parámetros físicos durante la deformación.

Los datos se procesan en un PC principal, mientras otro PC monitoriza el ensayo en tiempo real. La metodología Scrum organiza el trabajo en sprints semanales para asegurar entregas continuas y funcionales.

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

Luego de crear el entorno, instalar los requeriments.txt de esta manera, recuerde que debe estar en la ruta especificada del requirement:

![image](https://github.com/user-attachments/assets/ce1376c4-912c-44cc-97f8-099d5ec2d85b)

Luego es PostgreSQL crear una Base de datos llamada "Live" y colocar en password su contraseña de usuario de PostgreSQL.
Tmbien debe actualizar el archivo "settings.py" el cual esta en la siguiente ruta: C:\Users\Benja\OneDrive\Documentos\Consultoria-empresas\lifa-ultrasonido\Web-App\livewaveweb
![image](https://github.com/user-attachments/assets/d2136e4c-4c36-45d8-9bb3-06f28664eb9d)

Por ultimo crearse un super usuario o usuario para poder acceder al sitio Web. 
Debe tener en cuenta

## Requerimientos
Software, bibliotecas o entornos necesarios para que funcione el proyecto (ejemplo: versiones de Python, Node.js, etc.).
Crear un entorno en conda con la version de python==3.6. Y luego instalar los requeriments que en estos se contiene todas las librerias ocupadas, para hacer funcionar este proyecto en cualquier computador.
Para este software se utilizo la version de python-slugify==6.1.1
## Motor de base de datos utilizado
Para este proyecto utilizamos como motor de BD  PostgreSQL para la pagina WEB para almacenar a los usuarios que se vayan creando con su respectiva informacion y rol. Se recomienda la version de PostgreSQL==17.0 la cual se utilizo para el desarrollo de este proyecto

## Soporte visual

![image](https://github.com/user-attachments/assets/49f36865-22c3-4e3b-887f-6b430802f2d1)
Esta imagen representa el login de la pagina web del proyecto, en la caul estara un modulo de ensayo y un modulo de gestion de usuarios en donde se podran crear, editar  y eliminar usuarios. Las siguientes imagenes corresponderan a lo antes mencionado

### Modulo de gestion usuario
![image](https://github.com/user-attachments/assets/7aa8b83b-52c5-4c84-9cec-9dde561955a7)

![image](https://github.com/user-attachments/assets/669e6ad6-585b-438d-80bf-a672f9f392b9)

### Modulo de ensayo
Este modulo esta implementado con MongoDB el cual para este proyecto no fue implementado pormotivos externos que escapan del alcance de este proyecto, el modulo esta hecho con esta base de datos NOSQL y quedaria desarrollado para implementaciones futuras
![image](https://github.com/user-attachments/assets/d477f6f7-5038-4a08-96d4-a79c13fdd6ec)
![image](https://github.com/user-attachments/assets/96c7a705-9ba8-47f2-a604-19c97f319483)
Grafico generado a traves de datos incorporados en la base de datos, los cuales son simulados
![image](https://github.com/user-attachments/assets/abe3d33a-1676-4e14-ba66-578f7254d7e2)
![image](https://github.com/user-attachments/assets/7037b345-ba15-4b18-9cc0-ccb30e7aac67)
![image](https://github.com/user-attachments/assets/7cc810c8-b699-4e22-a1c5-c21ff7fb8a83)






### Interfaz GUI
Estas imagen corresponderan al diseño de la interfaz GUI la cual se abrira desde el sescritorio del computador del laboratorio. (Esta era el diseño de la interfaz, pero al final debido al tiempo, tambien priorizando más la felocidad del programa y que el computador del lab no soportaba la GUI)

### Ensayo

La imagen que se observa es la pagina de ensayo de la interfaz la cual iran todos los datos neciesarios para iniciar el ensayo  y selecionar el material utilizado en el ensayo y los datos que se obtendran mediante la camara.
![Imagen de WhatsApp 2024-11-14 a las 16 21 03_4003751e](https://github.com/user-attachments/assets/322521f4-4985-498b-bf20-a670d78b3561)


### Cargar datos
![Imagen de WhatsApp 2024-11-14 a las 16 20 55_20f0ee6c](https://github.com/user-attachments/assets/b68f687b-98da-419f-b32a-600552c38fd6)


En esta ventana de la interfaz verificaremos que se esten detectando los equipos para luego conectarlos, tambien se añadira los datos para el generdador de funciones y darle al boton guardar para que esta configuracion quede almacenada en la base de datos.


### Tarjeta de Adquicision
En esta parte de la interfaz se mostrara la grafica con los datos que se vayan recibiendo del a tarjeta de adquicision  donde se puede modificar los rangos del canal 1, canal 2 y Se puede modificar la muestra, luego estos cambos al darle al boton aplicar se palican para el ensayo y al darle al boton guardar esta configuracion se guarda en la base de datos o tambien la otra forma es cargar una configuracion ya echa.
![Imagen de WhatsApp 2024-11-14 a las 16 21 08_5d62bc80](https://github.com/user-attachments/assets/e3020b17-9cb4-48a5-93f2-9380304619e9)

### Equipos
PC1:
Este es el ordenador principal encargado de controlar y configurar los elementos del ensayo de tracción. A través de este equipo, se gestionan los datos provenientes de los sensores, la tarjeta de adquisición Phidget, el generador de funciones y la cámara. También envía la señal para iniciar la adquisición de datos en el PC2. Esta es la imagen del PC1.
![Imagen de WhatsApp 2024-10-16 a las 16 29 35_1b4afe43](https://github.com/user-attachments/assets/1a05ca57-5d4e-4746-9516-d7ba2f65a6e5)


PC2:
Este ordenador recibe y visualiza los datos del ensayo de tracción en tiempo real. Utiliza el software "WDW TEST CONTROL" para monitorear variables clave, como la fuerza aplicada y la deformación de la muestra. Se comunica con el PC1 para iniciar la adquisición de datos. La imagen del PC2.

![Imagen de WhatsApp 2024-11-15 a las 09 43 31_eceac5da](https://github.com/user-attachments/assets/61d903d4-3949-4c67-9fdc-2823509daf78)


Generador de funciones (DG1022):
Este dispositivo genera las ondas ultrasónicas que se transmiten a través de la muestra de acero. El generador de funciones permite configurar la amplitud, frecuencia y el número de ciclos de las señales ultrasónicas emitidas, y está conectado al sistema mediante USB para que se le puedan enviar comandos de control desde el PC1.
![Imagen de WhatsApp 2024-11-15 a las 09 43 31_2aaf044b](https://github.com/user-attachments/assets/d4c53af6-460f-4041-8344-80111781d0f2)



Máquina de tracción (HD-B612-10S):
La máquina de tracción es la encargada de aplicar la fuerza de tensión a la muestra de acero. Durante el ensayo, esta máquina estira la muestra hasta que se produce una fractura, y los datos de fuerza y desplazamiento se transmiten al sistema para su análisis.

![Imagen de WhatsApp 2024-11-15 a las 09 43 33_69a0aad3](https://github.com/user-attachments/assets/04a199f5-2378-4494-adbc-0be51e570308)


Cámara:
La cámara se utiliza para monitorear el espesor del material durante el ensayo. Ubicada frente a la muestra, captura cambios visuales en el espesor en tiempo real. Esto ayuda a calcular la deformación transversal del material mientras se lleva a cabo el ensayo.





### Diagrama 
En este diagrama de flujo se mostrara las conexiones que hay entre los equipos.
[Diagrama TestDetraccion.drawio (14).pdf](https://github.com/user-attachments/files/17781031/Diagrama.TestDetraccion.drawio.14.pdf)

![image](https://github.com/user-attachments/assets/70210933-b9b3-4ae7-b1c5-5381dce8f4e6)








