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

    # Renderizar la plantilla
    template_name = 'ensayo/list_tiempos_ensayo.html'
    return render(request, template_name, {
        'ensayo': ensayo,
        'tiempos': tiempos_paginados,
        'search': search,  # Pasar el término de búsqueda a la plantilla
        'page': page,      # Pasar la página actual
    })





def detalle_tiempo(request, tiempo_id):
    mongo_db = settings.MONGO_DB
    ensayos_collection = mongo_db.ensayo  # Colección de ensayos

    # Obtener el ensayo que contiene el tiempo específico
    ensayo = ensayos_collection.find_one({"tiempos.tiempo_id": tiempo_id})

    # Buscar el tiempo específico dentro del ensayo
    tiempo = next((t for t in ensayo['tiempos'] if t['tiempo_id'] == tiempo_id), None)


    return render(request, 'ensayo/detalle_tiempo.html', {
        'ensayo': ensayo,
        'tiempo': tiempo,
        
    })


def list_ensayo_deactivate(request, page=None, search=""):
    # Conectar a MongoDB
    mongo_db = settings.MONGO_DB
    ensayos_collection = mongo_db.ensayo  # Colección de ensayos

    # Obtener la página actual
    page = request.GET.get('page', 1)

    # Obtener la cadena de búsqueda desde el parámetro GET (en la URL)
    search = request.GET.get('search', '').strip()  # Limpiar la búsqueda

    # Número de elementos por página
    num_elemento = 10

    # Crear una consulta base para ensayos desactivados
    query = {"estado_ensayo": "Deactivate"}

    # Si hay una búsqueda, agregarla a la consulta
    if search:
        query["nombre_ensayo"] = {"$regex": search, "$options": "i"}  # Búsqueda insensible a mayúsculas

    # Obtener todos los ensayos desactivados de MongoDB, ordenados por `fecha_ensayo`
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
    ensayos_collection = mongo_db.ensayo  # Colección de ensayos

    # Intentar actualizar el ensayo por su _id
    try:
        result = ensayos_collection.update_one(
            {"_id": ObjectId(ensayo_id)},
            {"$set": {"estado_ensayo": "Deactivate"}}
        )

        if result.modified_count > 0:
            return redirect('list_ensayo_active')  # Redirigir a la lista de ensayos activos
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





    






