from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from ensayo.models import *
from datetime import datetime,timedelta
from django.db.models import Avg, Count, Q
#from registration.models import Profile
from django.urls import reverse_lazy
from core.views import *
# Create your views here.
import xlwt
import pandas as pd
from django.contrib.auth.models import User 
from extensiones.validacion import *
from django.core.paginator import Paginator
from pymongo import ASCENDING
from django.conf import settings
from bson.objectid import ObjectId
from django.shortcuts import render
from django.http import Http404
from django.conf import settings



def list_ensayo_active(request, page=None, search=""):
    # Conectar a MongoDB
    mongo_db = settings.MONGO_DB
    ensayos_collection = mongo_db.ensayo  # Colección de ensayos

    # Obtener la página actual
    page = request.GET.get('page', 1)

    # Obtener la cadena de búsqueda desde el parámetro GET
    search = request.GET.get('search', '').strip()  # Limpiar la búsqueda

    # Número de elementos por página
    num_elemento = 10

    # Crear una consulta base para ensayos activos
    query = {"estado_ensayo": "Activa"}

    # Si hay una búsqueda, agregarla a la consulta
    if search:
        query["nombre_ensayo"] = {"$regex": search, "$options": "i"}  # Búsqueda insensible a mayúsculas

    # Obtener todos los ensayos activos de MongoDB, ordenados por `fecha_ensayo`
    ensayo_all = ensayos_collection.find(query).sort("fecha_ensayo", ASCENDING)

    # Contar documentos que coinciden con la consulta
    total_ensayos = ensayos_collection.count_documents(query)

    # Paginación
    ensayos_con_id = []
    for ensayo in ensayo_all:
        ensayo['id'] = str(ensayo['_id'])  # Convertir ObjectId a cadena
        ensayos_con_id.append(ensayo)

    paginator = Paginator(ensayos_con_id, num_elemento)  # Convertir a lista para paginar
    ensayo_list = paginator.get_page(page)

    # Renderizar la plantilla
    template_name = 'ensayo/list_ensayo_active.html'
    print(f"Total ensayos activos encontrados: {total_ensayos}")
    print(f"query: {search}")

    return render(request, template_name, {
        'ensayo_list': ensayo_list,
        'paginator': paginator,
        'page': page,
        'search': search,
        'total_ensayos': total_ensayos,
    })



def list_tiempos_ensayo(request, ensayo_id, page=None, search=""):
    # Conectar a MongoDB
    mongo_db = settings.MONGO_DB
    ensayos_collection = mongo_db.ensayo  # Colección de ensayos

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
        ensayo = ensayos_collection.find_one({"_id": ObjectId(ensayo_id)})
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
    start_idx = (int(page) - 1) * num_elementos
    end_idx = start_idx + num_elementos
    tiempos_paginados = tiempos[start_idx:end_idx]

    template_name = 'ensayo/list_tiempos_ensayo.html'
    return render(request, template_name, {
        'ensayo': ensayo,
        'tiempos': tiempos_paginados,
        'search': search,  
        'page': page,      
    })

def grafico(request, ensayo_id):
    mongo_db = settings.MONGO_DB
    ensayos_collection = mongo_db.ensayo

    # Obtener el ensayo por su _id
    try:
        ensayo = ensayos_collection.find_one({"_id": ObjectId(ensayo_id)})
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
            {"campo1": tiempo.get("valor"), "campo2": tiempo.get("fuerza")}
            for tiempo in ensayo.get("tiempos", [])
        ]
        titulo = "Gráfico de Tiempo vs Fuerza (Opción 2)"
    elif opcion == 'opcion3':
        # Opción 3: Modifica los datos según esta opción
        datos = [
            {"campo1": tiempo.get("valor"), "campo2": tiempo.get("fuerza")}
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





def detalle_tiempo(request, tiempo_id):
    mongo_db = settings.MONGO_DB
    ensayos_collection = mongo_db.ensayo  

    ensayo = ensayos_collection.find_one({"tiempos.tiempo_id": tiempo_id})

    tiempo = next((t for t in ensayo['tiempos'] if t['tiempo_id'] == tiempo_id), None)


    return render(request, 'ensayo/detalle_tiempo.html', {
        'ensayo': ensayo,
        'tiempo': tiempo,
        
    })


def list_ensayo_deactivate(request, page=None, search=""):
    mongo_db = settings.MONGO_DB
    ensayos_collection = mongo_db.ensayo 

    page = request.GET.get('page', 1)

    search = request.GET.get('search', '').strip()  
  
    num_elemento = 10

    query = {"estado_ensayo": "Deactivate"}


    if search:
        query["nombre_ensayo"] = {"$regex": search, "$options": "i"}  

    ensayo_all = ensayos_collection.find(query).sort("fecha_ensayo", ASCENDING)


    total_ensayos = ensayos_collection.count_documents(query)

    ensayos_con_id = []
    for ensayo in ensayo_all:
        ensayo['id'] = str(ensayo['_id'])  
        ensayos_con_id.append(ensayo)

    paginator = Paginator(ensayos_con_id, num_elemento)  
    ensayo_list = paginator.get_page(page)

    template_name = 'ensayo/list_ensayo_deactivate.html'
    print(f"Total ensayos desactivados encontrados: {total_ensayos}")
    print(f"query: {search}")

    return render(request, template_name, {
        'ensayo_list': ensayo_list,
        'paginator': paginator,
        'page': page,
        'search': search,
        'total_ensayos': total_ensayos,
    })


'''@login_required'''
def ensayo_main(request):
    #profiles = Profile.objects.get(user_id = request.user.id)
    #check_profile_ensayo(request, profiles)
    template_name = 'ensayo/ensayo_main.html'
    return render(request,template_name,{})
   


'''@login_required'''

def ensayo_deactivate(request, ensayo_id):
    mongo_db = settings.MONGO_DB
    ensayos_collection = mongo_db.ensayo  

    try:
        result = ensayos_collection.update_one(
            {"_id": ObjectId(ensayo_id)},
            {"$set": {"estado_ensayo": "Deactivate"}}
        )

        if result.modified_count > 0:
            return redirect('list_ensayo_active')  
        else:
            return render(request, 'ensayo/error.html', {'mensaje': 'No se encontró el ensayo o ya estaba desactivado.'})

    except Exception as e:
        return render(request, 'ensayo/error.html', {'mensaje': 'Error al desactivar el ensayo: ' + str(e)})


'''@login_required'''
def ensayo_activate(request, ensayo_id):
    mongo_db = settings.MONGO_DB
    ensayos_collection = mongo_db.ensayo  # Colección de ensayos

    # Intentar actualizar el ensayo por su _id
    try:
        result = ensayos_collection.update_one(
            {"_id": ObjectId(ensayo_id)},
            {"$set": {"estado_ensayo": "Activa"}}
        )

        if result.modified_count > 0:
            return redirect('list_ensayo_active')  # Redirigir a la lista de ensayos activos
        else:
            return render(request, 'ensayo/error.html', {'mensaje': 'No se encontró el ensayo o ya estaba desactivado.'})

    except Exception as e:
        return render(request, 'ensayo/error.html', {'mensaje': 'Error al desactivar el ensayo: ' + str(e)})



# Vista para agregar rut a ensayo
def agregar_rut_ensayo(request, ensayo_id):
    mongo_db = settings.MONGO_DB
    ensayos_collection = mongo_db.ensayo  # Colección de ensayos

    if request.method == 'POST':
        rut = request.POST.get('rut', '').strip()

        # Validar que el RUT no esté vacío
        if not rut:
            messages.error(request, "El RUT no puede estar vacío.")
            return redirect('list_ensayo_active')  # Redirigir a la lista de ensayos

        try:
            # Verificar que el RUT exista en la base de datos de Django (modelo User)
            user = User.objects.get(rut=rut)

            # Obtener el ensayo por su _id
            ensayo = ensayos_collection.find_one({"_id": ObjectId(ensayo_id)})
            if not ensayo:
                messages.error(request, "Ensayo no encontrado.")
                return redirect('list_ensayo_active')  # Redirigir a la lista de ensayos

            # Aquí asociamos el RUT al ensayo
            print("aa")
            ensayos_collection.update_one(
                {"_id": ObjectId(ensayo_id)},
                {"$set": {"rut_asociado": rut}}  # Asociamos el RUT al ensayo
            )

            messages.success(request, f"El RUT {rut} ha sido asociado al ensayo correctamente.")
            return redirect('list_ensayo_active')  # Redirigir a la lista de ensayos

        except User.DoesNotExist:
            print("aaaaaaa")
            # Si no existe el RUT en la base de datos de Django
            messages.error(request, "El RUT no existe en el sistema.")
            return redirect('list_ensayo_active')  # Redirigir a la lista de ensayos

    else:
        return redirect('list_ensayo_active')  # Si no es una solicitud POST, redirigir


    






