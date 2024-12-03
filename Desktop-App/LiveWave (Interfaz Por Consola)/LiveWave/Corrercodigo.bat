@echo off
REM Activar el entorno de Miniconda
call D:\anaconda3\Scripts\activate.bat py3qt

REM Ir al directorio donde está tu script
cd /d C:\Users\AcuphyLab\Desktop\LiveWave\LiveWave

REM Ejecutar el script Python
python Menu.py
REM Mantener la ventana abierta si ocurre un error
pause
