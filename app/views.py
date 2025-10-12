from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Curso, Inscripcion, Carrito, Modulo, Unidad, Pregunta, Opcion, RespuestaUsuario, UnidadCompletada


try:
    from .forms import CustomUserCreationForm
except ImportError:
    class CustomUserCreationForm:
        pass  # Dummy class if not provided


def inicio(request):
    return render(request, "inicio.html")


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Cuenta creada como {user.role}")
            return redirect("inicio")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenido {user.username} ({user.role})")
            return redirect("inicio")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión")
    return redirect("login")


@login_required
def catalogo(request):
    cursos = Curso.objects.all()
    return render(request, "catalogo.html", {
        "cursos": cursos,
        "role": request.user.role
    })


@login_required
def inscribirse(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.user.role == "estudiante":
        Inscripcion.objects.get_or_create(estudiante=request.user, curso=curso)
        messages.success(request, f"Te has inscrito en {curso.titulo}")
    return redirect("mis_cursos")


@login_required
def mis_cursos(request):
    if request.user.role == "estudiante":
        inscripciones = Inscripcion.objects.filter(estudiante=request.user)
        cursos = [i.curso for i in inscripciones]
    else:
        cursos = Curso.objects.filter(profesor=request.user)
    return render(request, "mis_cursos.html", {"cursos": cursos})


@login_required
def carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    cursos = carrito.cursos.all()
    total = carrito.total()
    return render(request, "carrito.html", {"cursos": cursos, "total": total})


@login_required
def comprar_carrito(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    for curso in carrito.cursos.all():
        Inscripcion.objects.get_or_create(estudiante=request.user, curso=curso)
    carrito.cursos.clear()
    return redirect("mis_cursos")


@login_required
def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    
    
    unidades = curso.unidades.all().prefetch_related('preguntas__opciones')
    
    
    unidades_ids = unidades.values_list('id', flat=True) 

    
    unidades_completadas_ids = UnidadCompletada.objects.filter(
        usuario=request.user,
        unidad__curso=curso
    ).values_list('unidad_id', flat=True)

    
    respuestas_usuario = RespuestaUsuario.objects.filter(
        usuario=request.user, 
        pregunta__unidad__id__in=unidades_ids 
    )
    respuestas_dict = {r.pregunta_id: r for r in respuestas_usuario}

    return render(request, 'detalle_curso.html', {
        'curso': curso,
        'unidades': unidades,
        'respuestas_usuario': respuestas_dict,
        
        'unidades_completadas_ids': list(unidades_completadas_ids), 
    })


@login_required
def responder_unidad(request, unidad_id):
    unidad = get_object_or_404(Unidad, id=unidad_id)
    preguntas = unidad.preguntas.all()

    if request.method == 'POST':
        for pregunta in preguntas:
            opcion_id = request.POST.get(f'pregunta_{pregunta.id}')
            if opcion_id:
                opcion = get_object_or_404(Opcion, id=opcion_id)
                RespuestaUsuario.objects.update_or_create(
                    usuario=request.user,
                    pregunta=pregunta,
                    defaults={'opcion': opcion}
                )

        total_preguntas = preguntas.count()
        respuestas_dadas = RespuestaUsuario.objects.filter(usuario=request.user, pregunta__unidad=unidad)
        total_respondidas = respuestas_dadas.count()

        if total_preguntas > 0 and total_respondidas == total_preguntas:
            
            total_correctas = respuestas_dadas.filter(opcion__es_correcta=True).count()
            
            
            if total_correctas == total_preguntas:
                UnidadCompletada.objects.get_or_create(usuario=request.user, unidad=unidad)
                messages.success(request, f"¡Unidad '{unidad.titulo}' completada con éxito! 🎉")
            else:
                UnidadCompletada.objects.filter(usuario=request.user, unidad=unidad).delete()
                messages.warning(
                    request,
                    f"Respuestas guardadas. Tienes {total_correctas} de {total_preguntas} correctas. Inténtalo de nuevo."
                )

        return redirect('responder_unidad', unidad_id=unidad.id)

    respuestas_usuario = RespuestaUsuario.objects.filter(usuario=request.user, pregunta__unidad=unidad)
    respuestas_dict = {r.pregunta_id: r for r in respuestas_usuario}
    completada = UnidadCompletada.objects.filter(usuario=request.user, unidad=unidad).exists()

    return render(request, 'unidad_cuestionario.html', {
        'unidad': unidad,
        'preguntas': preguntas,
        'respuestas_usuario': respuestas_dict,
        'completada': completada
    })


@login_required
def agregar_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if curso.es_gratuito:
        Inscripcion.objects.get_or_create(estudiante=request.user, curso=curso)
        messages.success(request, f"Te has inscrito en {curso.titulo}")
        return redirect('mis_cursos')
    else:
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        carrito.cursos.add(curso)
        messages.success(request, f"{curso.titulo} agregado al carrito")
        return redirect('carrito')
