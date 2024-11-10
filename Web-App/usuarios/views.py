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
# Create your views here.

@login_required
def user_list(request):
    # Verificación de permisos
    if not request.user.is_staff:
        messages.error(request, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('home')
    
    search_query = request.GET.get('search', '').strip().lower()
    role_filter = request.GET.get('role', '')

    # Filtrar usuarios activos
    users = User.objects.filter(is_active=True)
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(carrera__icontains=search_query) |
            Q(rut__icontains=search_query)
        )
    if role_filter:
        users = users.filter(is_staff=(role_filter == 'Docente'))
    
    # Obtener el usuario actual
    current_user = request.user
    users = users.order_by('-id') 

    # Filtrar y mover al usuario actual al principio de la lista
    users = users.order_by(
        'id' if current_user.is_staff else '-id'
    )
    
    paginator = Paginator(users, 10)
    page = request.GET.get('page', 1)
    try:
        users = paginator.page(page)
    except:
        users = paginator.page(1)

    datos = {'usuarios': users, 'search_query': search_query, 'role_filter': role_filter}
    return render(request, 'usuarios/user_list.html', {'datos': datos})

@login_required

def add_user(request):
    profile = User.objects.get(id=request.user.id)
    if not profile.is_staff:
        return redirect('home')
        
    
    if request.method == 'POST':
        form = CustomAddUserForm(request.POST)
        correo = request.POST.get('email')
        rut=request.POST.get('rut')
        if User.objects.filter(email=correo).exists():
             messages.error(request, "Correo electronico en uso")
             return render(request, 'usuarios/add_user.html', {'form': form})
        

        if User.objects.filter(email=correo).exists():
             messages.error(request, "Correo electronico en uso")
             return render(request, 'usuarios/add_user.html', {'form': form})
        if validar_email(correo)==False:
             messages.error(request, "El correo no ha sido ingresado icorrectamente")
             return render(request, 'usuarios/add_user.html', {'form': form}) 
        if validar_rut(rut)==False:
            messages.error(request, "El rut ingresado no es valido")
            return render(request, 'usuarios/add_user.html', {'form': form})    
        


        if form.is_valid():
            contraseña_aleatoria = BaseUserManager().make_random_password()
            form.save(commit=False)
            form.setPassword(contraseña_aleatoria)
            messages.success(request, "Usuario añadido con exito")
            send_email_confirm(request, contraseña_aleatoria)
            return redirect('user_list') 
        else:
            # Si el formulario no es válido, volver a mostrar el formulario con errores
            return render(request, 'usuarios/add_user.html', {'form': form})
    else:
        # Si la solicitud no es POST, mostrar un formulario en blanco
        form = CustomAddUserForm()  
        return render(request, 'usuarios/add_user.html', {'form': form})


def send_email_confirm(request, aleatoria):
    print(aleatoria)
    username = request.POST['username']
    email = request.POST['email']
    template = get_template('email/adduser_email_confirm.html')
    content = template.render({'username': username, 'aleatoria': aleatoria})


    msg = EmailMultiAlternatives(
        'Registro completado',
        '',
        settings.EMAIL_HOST_USER,
        [email]
    )

    msg.attach_alternative(content, 'text/html')
    msg.send()




@login_required

def delete_user(request, id_users):
    profile = User.objects.get(id=request.user.id)
    if not profile.is_staff:
        messages.error(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('home')
    user = User.objects.get(pk=id_users)
    user.is_active = False
    user.save()
    messages.success(request, "Usuario eliminado correctamente")
    return redirect('user_list')


@login_required

def edit_user(request, id):
    profile = User.objects.get(id=request.user.id)
    if not profile.is_staff:
        messages.error(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('home')
    
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        

        # Obtener los datos del formulario
        username = request.POST.get('username').strip()
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        rut = request.POST.get('rut').strip()
        email = request.POST.get('email').strip()
        is_staff = request.POST.get('is_staff') 
        carrera = request.POST.get('carrera')
        phone = request.POST.get('phone') 

        # Validar que los campos no estén vacíos
        if not username or not first_name or not last_name or not rut or not email or not is_staff:
            messages.error(request, 'Ningún campo debe estar en blanco.')
            return redirect('edit_user', id=id)
        
        # Verificar si el nuevo nombre de usuario ya existe, excluyendo al usuario actual
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return redirect('edit_user', id=id)
        
        # Verificar si el nuevo correo ya existe, excluyendo al usuario actual
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "Correo electrónico en uso")
            return redirect('edit_user', id=id)
        
        # Validación de rut
        if not validar_rut(rut):
            messages.error(request, "El rut no ha sido ingresado correctamente, recuerde: sin puntos y con guion")
            return redirect('edit_user', id=id)
        
        # Validar que los campos no estén vacíos
        if not username or not first_name or not last_name or not rut or not email:
            messages.error(request, 'Ningún campo debe estar en blanco.')
            return redirect('edit_user', id=id)

        # Actualizar los datos del usuario
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.rut = rut
        user.email = email
        user.is_staff = is_staff
        user.carrera = carrera
        user.phone = phone

        user.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('user_list')
    
    else:
        # Renderizar el formulario con los datos del usuario
        return render(request, 'usuarios/edit_user.html', {'user': user})
    

def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_staff:
        rol = "Docente"
    else:
        rol = "Estudiante"

    data = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "rut": user.rut,
        "rol": rol,
        "carrera": user.carrera,
        "phone": str(user.phone)
    }
    return JsonResponse(data)