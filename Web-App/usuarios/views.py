from django.shortcuts import get_object_or_404, render, redirect, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import BaseUserManager
from user.models import User
from django.http import HttpResponse, Http404, JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.hashers import make_password
from django.template.loader import get_template
from django.contrib import messages
from django.conf import settings
from .forms import CustomAddUserForm
from django.core.paginator import Paginator
from extensiones.validacion import *
from django.db.models import Q


@login_required
def lista_de_usuarios(request):
    # Se verifica si el usuario tiene permisos de administrador
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta área')
        return redirect('home')
    
    # Se obtiene la búsqueda y el filtro de rol desde la URL (GET)
    consulta_busqueda = request.GET.get('search', '').strip().lower()
    filtro_rol = request.GET.get('role', '')

    # Se obtienen solo los usuarios activos
    usuarios = User.objects.filter(is_active=True)
    
    # Si hay algo para buscar, se aplica el filtro de búsqueda
    if consulta_busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=consulta_busqueda) |  # Se busca en el nombre de usuario
            Q(first_name__icontains=consulta_busqueda) |  # Se busca en el primer nombre
            Q(last_name__icontains=consulta_busqueda) |  # Se busca en el apellido
            Q(carrera__icontains=consulta_busqueda) |  # Se busca en la carrera
            Q(rut__icontains=consulta_busqueda)  # Se busca en el RUT
        )
    
    # Si hay un filtro de rol (como 'Docente'), se aplica
    if filtro_rol:
        usuarios = usuarios.filter(is_staff=(filtro_rol == 'Docente'))
    
    # Se obtiene el usuario actual
    usuario_actual = request.user
    usuarios = usuarios.order_by('-id')  # Se ordenan de más reciente a más antiguo

    # Si el usuario no es admin, se pone al principio de la lista
    usuarios = usuarios.order_by(
        'id' if usuario_actual.is_staff else '-id'  # Si es admin, no cambia el orden
    )
    
    # Se hace la paginación (10 usuarios por página)
    paginator = Paginator(usuarios, 10)
    pagina = request.GET.get('page', 1)  # Se obtiene el número de página
    try:
        usuarios = paginator.page(pagina)  # Se muestra la página solicitada
    except:
        usuarios = paginator.page(1)  # Si hay error, se muestra la primera página

    # Se preparan los datos para renderizar en la plantilla
    datos = {'usuarios': usuarios, 'consulta_busqueda': consulta_busqueda, 'filtro_rol': filtro_rol}
    
    # Se renderiza la plantilla con los datos
    return render(request, 'usuarios/lista_de_usuarios.html', {'datos': datos})

@login_required

def agregar_usuario(request):
    # Verificar que el usuario actual es staff (Docente)
    perfil = User.objects.get(id=request.user.id)
    if not perfil.is_staff:
        return redirect('inicio')

    if request.method == 'POST':
        formulario = CustomAddUserForm(request.POST)
        correo = request.POST.get('email')
        rut = request.POST.get('rut')

        # Validaciones del formulario
        if User.objects.filter(email=correo, is_active=True).exists():
            messages.error(request, "Correo electrónico en uso")
            return render(request, 'usuarios/agregar_usuario.html', {'formulario': formulario})
        
        # Validaciones del formulario
        if User.objects.filter(rut=rut, is_active=True).exists():
            messages.error(request, "El rut ya esta en uso")
            return render(request, 'usuarios/agregar_usuario.html', {'formulario': formulario})


        if not validar_email(correo):
            messages.error(request, "El correo no ha sido ingresado correctamente")
            return render(request, 'usuarios/agregar_usuario.html', {'formulario': formulario})

        if not validar_rut(rut):
            messages.error(request, "El RUT ingresado no es válido")
            return render(request, 'usuarios/agregar_usuario.html', {'formulario': formulario})

        # Si el formulario es válido, lo procesamos
        if formulario.is_valid():
            # Generar una contraseña aleatoria
            contraseña_aleatoria = BaseUserManager().make_random_password()
            usuario = formulario.save(commit=False)
            usuario.set_password(contraseña_aleatoria)
            usuario.save()
            messages.success(request, "Usuario añadido con éxito")
            enviar_email(request, contraseña_aleatoria)  # Enviar email con la contraseña

            return redirect('lista_de_usuarios')  # Redirigir al listado de usuarios
        else:
            return render(request, 'usuarios/agregar_usuario.html', {'formulario': formulario})  # Si el formulario no es válido

    else:
        formulario = CustomAddUserForm()  # Crear un formulario vacío para GET
        return render(request, 'usuarios/agregar_usuario.html', {'formulario': formulario})


def enviar_email(request, aleatoria):
    print(aleatoria)
    username = request.POST['username']
    email = request.POST['email']
    template = get_template('email/email_de_confirmacion.html')
    content = template.render({'username': username, 'aleatoria': aleatoria})


    mensaje = EmailMultiAlternatives(
        'Registro completado',
        '',
        settings.EMAIL_HOST_USER,
        [email]
    )

    mensaje.attach_alternative(content, 'text/html')
    mensaje.send()




@login_required

def eliminar_usuario(request, id_users):
    # Verificar que el usuario actual es staff (Docente)
    perfil = User.objects.get(id=request.user.id) 
    if not perfil.is_staff:
        messages.error(request, 'Intenta ingresar a una area para la que no tiene permisos') 
        return redirect('home')  # Redirigir a la página de inicio si no tiene permisos

    # Obtener el usuario que se va a eliminar a partir de su ID
    usuario = User.objects.get(pk=id_users)  

    # Cambiar el estado del usuario para que no esté activo
    usuario.is_active = False 
    usuario.save()  # Guardar los cambios en la base de datos

    # Mostrar un mensaje de éxito informando que el usuario fue eliminado
    messages.success(request, "Usuario eliminado correctamente")  

    # Redirigir a la lista de usuarios después de eliminar al usuario
    return redirect('lista_de_usuarios') 



@login_required

def editar_usuario(request, id):
    # Verificar que el usuario actual es staff (Docente)
    profile = User.objects.get(id=request.user.id)
    if not profile.is_staff:
        messages.error(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('home') # Redirigir a la página de inicio si no tiene permisos
    
    usuario = get_object_or_404(User, id=id)
    if request.method == 'POST':
        

        # Obtener los datos del formulario
        username = request.POST.get('username').strip()
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        rut = request.POST.get('rut').strip()
        email = request.POST.get('email').strip()
        is_staff = request.POST.get('is_staff') 
        carrera = request.POST.get('carrera')
        telefono = request.POST.get('telefono') 

        # Validar que los campos no estén vacíos
        if not username or not first_name or not last_name or not rut or not email or not is_staff:
            messages.error(request, 'Ningún campo debe estar en blanco.')
            return redirect('editar_usuario', id=id)
        
        # Verificar si el nuevo nombre de usuario ya existe, excluyendo al usuario actual
        if User.objects.filter(username=username , is_active=True).exclude(id=usuario.id).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return redirect('editar_usuario', id=id)
        
        # Verificar si el nuevo nombre de usuario ya existe, excluyendo al usuario actual
        if User.objects.filter(rut=rut , is_active=True).exclude(id=usuario.id).exists():
            messages.error(request, 'El rut ya esta en uso')
            return redirect('editar_usuario', id=id)
        
        # Verificar si el nuevo correo ya existe, excluyendo al usuario actual
        if User.objects.filter(email=email , is_active=True).exclude(id=usuario.id).exists():
            messages.error(request, "Correo electrónico en uso")
            return redirect('editar_usuario', id=id)
        
        # Validación de rut
        if not validar_rut(rut):
            messages.error(request, "El rut no ha sido ingresado correctamente, recuerde: sin puntos y con guion")
            return redirect('editar_usuario', id=id)
        
        if not validar_numCelular(telefono):
            messages.error(request, "El número de teléfono ingresado no es valido")
            return redirect('editar_usuario', id=id)
        
        # Validar que los campos no estén vacíos
        if not username or not first_name or not last_name or not rut or not email:
            messages.error(request, 'Ningún campo debe estar en blanco.')
            return redirect('editar_usuario', id=id)

        # Actualizar los datos del usuario
        usuario.username = username
        usuario.first_name = first_name
        usuario.last_name = last_name
        usuario.rut = rut
        usuario.email = email
        usuario.is_staff = is_staff
        usuario.carrera = carrera
        usuario.telefono = telefono

        usuario.save() # Guardar los cambios en la base de datos
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('lista_de_usuarios') 
    
    else:
        # Renderizar el formulario con los datos del usuario
        return render(request, 'usuarios/editar_usuario.html', {'usuario': usuario})
    

def detalles_usuario(request, user_id):
    #Verificar si el usuario existe
    usuario = get_object_or_404(User, id=user_id)

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