from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from ensayo.models import *
from core.views import *
from user.models import User
from extensiones.validacion import *
from django.core.paginator import Paginator
from pymongo import ASCENDING
from django.conf import settings
from bson.objectid import ObjectId
from django.shortcuts import render
from django.conf import settings
from extensiones.validacion import *
from django.http import JsonResponse


@login_required
def listado_ensayo_active(request, page=None, search=""):
    # Conectar a MongoDB
    mongo_db = settings.MONGO_DB
    ensayos_colleccion = mongo_db.ensayo  # Colección de ensayos

    # Obtener la página actual
    page = request.GET.get('page', 1)

    # Obtener la cadena de búsqueda desde el parámetro GET

    search = request.GET.get('search', '').strip()  # Limpiar la búsqueda

    # Número de elementos por página
    num_elemento = 10
    # Crear una consulta base para ensayos activos
    consulta = {"estado_ensayo": "Activa"}

    # Si hay una búsqueda, agregarla a la consulta
    if search:
        consulta["nombre_ensayo"] = {"$regex": search, "$options": "i"}  # Búsqueda insensible a mayúsculas

    # Obtener todos los ensayos activos de MongoDB, ordenados por `fecha_ensayo
    ensayos = ensayos_colleccion.find(consulta).sort("fecha_ensayo", ASCENDING)

    # Contar documentos que coinciden con la consulta
    total_ensayos = ensayos_colleccion.count_documents(consulta)

    # Paginación
    ensayos_con_id = []
    for ensayo in ensayos:
        ensayo['id'] = str(ensayo['_id'])  # Convertir ObjectId a cadena
        ensayos_con_id.append(ensayo)

    paginator = Paginator(ensayos_con_id, num_elemento)  # Convertir a listadoa para paginar
    ensayo_listado = paginator.get_page(page)
    # Renderizar la plantilla
    template_name = 'ensayo/listado_ensayo_active.html'

    return render(request, template_name, {
        'ensayo_listado': ensayo_listado,
        'paginator': paginator,
        'page': page,
        'search': search,
        'total_ensayos': total_ensayos,
    })


@login_required
def listado_tiempos_ensayo(request, ensayo_id, page=None, search=""):
    # Conectar a MongoDB
    mongo_db = settings.MONGO_DB
    ensayos_colleccion = mongo_db.ensayo  # Colección de ensayos

    # Obtener la página actual
    page = request.GET.get('page', 1)

    # Obtener la cadena de búsqueda desde POST si existe
    if request.method == 'POST':
        search = request.POST.get('search', '').strip()  # Limpiar la búsqueda
        page = 1  # Reiniciar a la primera página en la búsqueda

    # Número de elementos por página
    num_elementos = 10

    # Intentar obtener el ensayo por su _id
    try:
        ensayo = ensayos_colleccion.find_one({"_id": ObjectId(ensayo_id)})
    except Exception as e:
        return render(request, 'ensayo/error.html', {'mensaje': 'Error al buscar el ensayo.'})

    # Manejar el caso en que no se encuentre el ensayo
    if ensayo is None:
        return render(request, 'ensayo/error.html', {'mensaje': 'Ensayo no encontrado.'})

    # Obtener los tiempos del ensayo
    tiempos = ensayo.get('tiempos', [])

    # Si se proporciona un término de búsqueda, filtrar los tiempos
    if search:
        # Filtrar los tiempos que coincidan con el término de búsqueda
        tiempos = [tiempo for tiempo in tiempos if search.lower() in str(tiempo.get('valor', '')).lower()]

    # Paginación
    inicio_index = (int(page) - 1) * num_elementos
    end_idx = inicio_index + num_elementos
    tiempos_paginados = tiempos[inicio_index:end_idx]

    template_name = 'ensayo/listado_tiempos_ensayo.html'
    return render(request, template_name, {
        'ensayo': ensayo,
        'tiempos': tiempos_paginados,
        'search': search,  
        'page': page,      
    })

@login_required
def grafico(request, ensayo_id):
    #Conexión a Mongo
    mongo_db = settings.MONGO_DB
    #Coleccion a usar
    ensayos_colleccion = mongo_db.ensayo

    # Obtener el ensayo por su _id
    try:
        ensayo = ensayos_colleccion.find_one({"_id": ObjectId(ensayo_id)})
    except Exception as e:
        return render(request, 'ensayo/error.html', {'mensaje': 'Error al buscar el ensayo.'})

    # Manejar el caso en que no se encuentre el ensayo
    if ensayo is None:
        return render(request, 'ensayo/error.html', {'mensaje': 'Ensayo no encontrado.'})

    # Opción predeterminada si no se pasa ninguna opción
    opcion = request.POST.get('opcion', 'opcion1')

    # Configurar los datos según la opción seleccionada
    if opcion == 'opcion1':
        # Opción 1: Mostrar tiempo.valor en el eje X y fuerza en el eje Y
        datos = [
            {"campo1": tiempo.get("valor"), "campo2": tiempo.get("fuerza")}
            for tiempo in ensayo.get("tiempos", [])
        ]
        titulo = "Gráfico de Tiempo vs Fuerza (Opción 1)"
    elif opcion == 'opcion2':
        # Opción 2: (Puedes modificar los datos según esta opción)
        datos = [
            {"campo1": tiempo.get("valor"), "campo2": tiempo.get("time_of_fly")}
            for tiempo in ensayo.get("tiempos", [])
        ]
        titulo = "Gráfico de Tiempo vs Fuerza (Opción 2)"
    elif opcion == 'opcion3':
        # Opción 3: Modifica los datos según esta opción
        datos = [
            {"campo1": tiempo.get("valor"), "campo2": tiempo.get("stress")}
            for tiempo in ensayo.get("tiempos", [])
        ]
        titulo = "Gráfico de Tiempo vs Fuerza (Opción 3)"

    # Preparar los datos para el gráfico
    eje_x = [dato.get("campo1") for dato in datos]  # Extraer los valores para el eje X
    valores_y = [dato.get("campo2") for dato in datos]  # Extraer los valores para el eje Y

    # Pasar los datos a la plantilla
    datos_grafico = {
        "eje_x": eje_x,
        "valores_y": valores_y,
        "titulo": titulo,
        "ensayo_id": ensayo_id  # Aquí pasamos el ensayo.id a la plantilla
    }

    return render(request, 'ensayo/grafico.html', datos_grafico)


@login_required
def detalle_tiempo(request, tiempo_id):
    #Conexión a Mongodb
    mongo_db = settings.MONGO_DB
    #Coleccion a usar
    ensayos_colleccion = mongo_db.ensayo  

    #ensayo buscado por id
    ensayo = ensayos_colleccion.find_one({"tiempos.tiempo_id": tiempo_id})

    tiempo = next((t for t in ensayo['tiempos'] if t['tiempo_id'] == tiempo_id), None)


    return render(request, 'ensayo/detalle_tiempo.html', {
        'ensayo': ensayo,
        'tiempo': tiempo,
        
    })


@login_required
def listado_ensayo_deactivate(request, page=None, search=""):
    #Conexion a Mongodb
    mongo_db = settings.MONGO_DB

    #Coleccion a utilizar
    ensayos_colleccion = mongo_db.ensayo 

    page = request.GET.get('page', 1)

    search = request.GET.get('search', '').strip()  
  
    num_elemento = 10
    #ensayos desactivados
    consulta = {"estado_ensayo": "Deactivate"}


    if search:
        consulta["nombre_ensayo"] = {"$regex": search, "$options": "i"}  
    #Todos los ensayos desactivados ordenados por fecha de ensayo
    ensayos = ensayos_colleccion.find(consulta).sort("fecha_ensayo", ASCENDING)


    total_ensayos = ensayos_colleccion.count_documents(consulta)

    ensayos_con_id = []
    for ensayo in ensayos:
        ensayo['id'] = str(ensayo['_id'])  
        ensayos_con_id.append(ensayo)

    paginator = Paginator(ensayos_con_id, num_elemento)  
    ensayo_listado = paginator.get_page(page)

    template_name = 'ensayo/listado_ensayo_deactivate.html'

    return render(request, template_name, {
        'ensayo_listado': ensayo_listado,
        'paginator': paginator,
        'page': page,
        'search': search,
        'total_ensayos': total_ensayos,
    })


@login_required
def ensayo_main(request):
    template_name = 'ensayo/ensayo_main.html'
    return render(request,template_name,{})
   


@login_required
def ensayo_deactivate(request, ensayo_id):
    #Conexion a Mongo Db
    mongo_db = settings.MONGO_DB
    #Coleccion a utilizar
    ensayos_colleccion = mongo_db.ensayo  

    try:
        #Intenta cambiar estado de ensayo por su id
        resultado = ensayos_colleccion.update_one(
            {"_id": ObjectId(ensayo_id)},
            {"$set": {"estado_ensayo": "Deactivate"}}
        )
        #verifica la modificacion
        if resultado.modified_count > 0:
            return redirect('listado_ensayo_active')  


    except Exception as e:
        return redirect('listado_ensayo_active')





@login_required
def ensayo_activate(request, ensayo_id):
    mongo_db = settings.MONGO_DB
    ensayos_colleccion = mongo_db.ensayo  # Colección de ensayos

    # Intentar actualizar el ensayo por su _id
    try:
        resultado = ensayos_colleccion.update_one(
            {"_id": ObjectId(ensayo_id)},
            {"$set": {"estado_ensayo": "Activa"}}
        )

        if resultado.modified_count > 0:
            return redirect('listado_ensayo_deactivate')  # Redirigir a la listadoa de ensayos activos


    except Exception as e:
        return redirect('listado_ensayo_deactivate')


# Vista para agregar rut a ensayo
@login_required
def agregar_rut_ensayo(request, ensayo_id):
    mongo_db = settings.MONGO_DB
    ensayos_collection = mongo_db.ensayo  # Colección de ensayos

    if request.method == 'POST':
        rut = request.POST.get('rut', '').strip()
        print(f"RUT recibido: {rut}")  # Debug: Verifica el valor del RUT

        if not validar_rut(rut):
            messages.error(request, "El rut no ha sido ingresado correctamente, recuerde: sin puntos y con guion")
            return redirect('listado_ensayo_active')

        # Validar que el RUT no esté vacío
        if not rut:
            messages.error(request, "El RUT no puede estar vacío.")
            return redirect('listado_ensayo_active')

        try:
            # Verificar que el RUT exista en la base de datos de Django (modelo User)
            usuario = User.objects.filter(is_active=True)
            print(f"Usuario encontrado: {usuario}")  # Debug: Verifica el usuario encontrado

            # Obtener el ensayo por su _id
            ensayo = ensayos_collection.find_one({"_id": ObjectId(ensayo_id)})
            if not ensayo:
                messages.error(request, "Ensayo no encontrado.")
                return redirect('listado_ensayo_active')
            if not usuario:
                print("El usuario no existe en la base de datos")
            # Actualización en MongoDB
            result = ensayos_collection.update_one(
                {"_id": ObjectId(ensayo_id)},
                {"$set": {"rut_asociado": rut}}
            )

            # Verificación del resultado de la actualización
            if result.matched_count == 0:
                print("No se encontró ningún documento para actualizar.")
            if result.modified_count == 0:
                print("El documento no fue modificado.")

            messages.success(request, f"El RUT {rut} ha sido asociado al ensayo correctamente.")
            return redirect('listado_ensayo_active')

        except User.DoesNotExist:
            # Si no existe el RUT en la base de datos de Django
            messages.error(request, "El RUT no existe en el sistema.")
            return redirect('listado_ensayo_active')

    else:
        return redirect('listado_ensayo_active')
    

def detalles_usuario_por_rut(request, rut):
    #Verificar si el usuario existe
    try:
        usuario = User.objects.get(rut=rut, is_active=True)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado o inactivo'}, status=404)

    # Establecer variables para rol dependiendo si usuario es staff
    if usuario.is_staff:
        rol = "Docente"
    else:
        rol = "Estudiante"
    # Creación de diccionario de datos
    datos = {
        "username": usuario.username,
        "first_name": usuario.first_name,
        "last_name": usuario.last_name,
        "email": usuario.email,
        "rut": usuario.rut,
        "rol": rol,
        "carrera": usuario.carrera,
        "telefono": str(usuario.telefono)
    }
    return JsonResponse(datos)