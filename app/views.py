from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.conf import settings
from django.urls import reverse
from datetime import datetime
from django.http import JsonResponse


from .models import (
    Curso, Inscripcion, Carrito, Modulo, Unidad, Pregunta, Opcion,
    RespuestaUsuario, UnidadCompletada, CursoProfesor, CustomUser, Progreso, Pago,  ItemTienda, Inventario
)
from .forms import CursoForm



from django.views.decorators.csrf import csrf_exempt
from transbank.webpay.webpay_plus.transaction import Transaction, WebpayOptions
from transbank.common.integration_type import IntegrationType



try:
    from .forms import CustomUserCreationForm
except ImportError:
    class CustomUserCreationForm:
        pass



@login_required
def inicio(request):
    usuario = request.user
    gif_equipado = None

    # Buscamos un GIF equipado en su inventario
    inventario_gif = Inventario.objects.filter(
        usuario=usuario,
        item__tipo='GIF',
        equipado=True
    ).select_related('item').first()

    if inventario_gif and inventario_gif.item.archivo:
        gif_equipado = inventario_gif.item.archivo.url

    return render(request, "inicio.html", {
        "gif_equipado": gif_equipado
    })


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
    query = request.GET.get('q', '')  
    if query:
        cursos = Curso.objects.filter(titulo__icontains=query) 
    else:
        cursos = Curso.objects.all()
    return render(request, "catalogo.html", {"cursos": cursos, "query": query, "role": request.user.role})



@login_required
def inscribirse(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.user.role == "estudiante":
        Inscripcion.objects.get_or_create(estudiante=request.user, curso=curso)
        messages.success(request, f"Te has inscrito en {curso.titulo}")
    return redirect("mis_cursos")


@login_required
def mis_cursos(request):
    user = request.user

    if user.role == "estudiante":
        inscripciones = Inscripcion.objects.filter(estudiante=user)
        cursos = [i.curso for i in inscripciones]
        return render(request, "mis_cursos.html", {"cursos": cursos})

    elif user.role == "profesor":
        cursos_creados = Curso.objects.filter(profesor=user)
        cursos_supervisados = Curso.objects.filter(
            id__in=CursoProfesor.objects.filter(profesor=user).values_list('curso_id', flat=True)
        )
        cursos = (cursos_creados | cursos_supervisados).distinct()

        datos_cursos = []
        for curso in cursos:
            inscripciones = Inscripcion.objects.filter(curso=curso).select_related("estudiante")
            estudiantes = []
            for inscripcion in inscripciones:
                estudiante = inscripcion.estudiante
                total_unidades = curso.unidades.count()
                completadas = UnidadCompletada.objects.filter(
                    usuario=estudiante, unidad__curso=curso
                ).count()
                progreso = int((completadas / total_unidades * 100)) if total_unidades > 0 else 0
                estudiantes.append({
                    "nombre": estudiante.username,
                    "progreso": progreso,
                    "completadas": completadas,
                    "totales": total_unidades,
                })
            datos_cursos.append({"curso": curso, "estudiantes": estudiantes})

        return render(request, "mis_cursos_profesor.html", {"datos_cursos": datos_cursos})

    return render(request, "mis_cursos.html", {"cursos": []})


@login_required
def carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    cursos = carrito.cursos.all()
    total = carrito.total()
    return render(request, "carrito.html", {"cursos": cursos, "total": total})


@login_required
def agregar_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    if curso.precio == 0:  
        if request.method == "POST":
            codigo_profesor = request.POST.get("codigo_profesor", "").strip()
            profesor = None
            if codigo_profesor:
                profesor = CustomUser.objects.filter(
                    codigo_profesor=codigo_profesor, role='profesor'
                ).first()
            Inscripcion.objects.get_or_create(
                estudiante=request.user,
                curso=curso,
                defaults={"profesor_asignado": profesor}
            )
        messages.success(request, f"Te has inscrito correctamente en el curso: {curso.titulo}.")
        return redirect('mis_cursos')

    else:  
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        carrito.cursos.add(curso)
        messages.info(request, f"{curso.titulo} fue agregado a tu carrito.")
        return redirect('carrito')


@login_required
def eliminar_del_carrito(request, curso_id):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    curso = get_object_or_404(Curso, id=curso_id)
    carrito.cursos.remove(curso)
    messages.info(request, f"{curso.titulo} eliminado del carrito.")
    return redirect('carrito')


@login_required
def comprar_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    cursos = carrito.cursos.all()
    if not cursos:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('carrito')
    return redirect('pago_webpay')


@login_required
def pago_webpay(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    cursos = carrito.cursos.all()
    total = carrito.total()

    
    if not cursos:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('carrito')

    if total == 0:
        for curso in cursos:
            Inscripcion.objects.get_or_create(estudiante=request.user, curso=curso)
            Progreso.objects.get_or_create(estudiante=request.user, curso=curso)
        carrito.cursos.clear()
        messages.success(request, " Te has inscrito correctamente en tus cursos gratuitos.")
        return redirect('mis_cursos')

    
    commerce_code = "597055555532"
    api_key = "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"
    options = WebpayOptions(commerce_code, api_key, IntegrationType.TEST)

    tx = Transaction(options)

    response = tx.create(
        buy_order=str(request.user.id) + "_order",
        session_id=str(request.user.id),
        amount=total,
        return_url=request.build_absolute_uri("/confirmar_pago/")
    )

    return render(request, "pago_webpay.html", {"url": response["url"], "token": response["token"]})

@csrf_exempt
def confirmar_pago(request):
    token = request.GET.get("token_ws") or request.POST.get("token_ws")

    if not token:
        messages.error(request, "No se recibió el token de pago.")
        return redirect("carrito")

    commerce_code = "597055555532"
    api_key = "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"
    options = WebpayOptions(commerce_code, api_key, IntegrationType.TEST)
    tx = Transaction(options)

    try:
        response = tx.commit(token)

        if response["status"] == "AUTHORIZED":
            carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
            cursos = carrito.cursos.all()

            
            Pago.objects.create(
                usuario=request.user,
                orden=response["buy_order"],
                monto=response["amount"],
                codigo_autorizacion=response["authorization_code"],
                estado=response["status"]
            )

            
            for curso in cursos:
                Inscripcion.objects.get_or_create(
                    estudiante=request.user,
                    curso=curso
                )

            progreso, _ = Progreso.objects.get_or_create(
                estudiante=request.user,
                curso=curso)
            
            progreso.actualizar_progreso()
    
            
            carrito.cursos.clear()

            
            context = {
                "response": response,
                "cursos": cursos,
                "usuario": request.user,
                "monto": response["amount"],
            }
            return render(request, "comprobante_pago.html", context)

        else:
            messages.error(request, "El pago fue rechazado o falló.")
            return render(request, "pago_fallido.html", {"response": response})

    except Exception as e:
        messages.error(request, f"Error procesando el pago: {e}")
        return redirect("carrito")

@login_required
def historial_pagos(request):
    pagos = Pago.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'historial_pagos.html', {'pagos': pagos})



@login_required
def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    unidades = curso.unidades.all()
    completadas = UnidadCompletada.objects.filter(
        usuario=request.user, unidad__in=unidades
    ).values_list('unidad_id', flat=True)

    total = unidades.count()
    porcentaje = int(len(completadas) / total * 100) if total > 0 else 0

    return render(request, 'detalle_curso.html', {
        'curso': curso,
        'unidades': unidades,
        'unidades_completadas_ids': list(completadas),
        'porcentaje': porcentaje,
    })

@login_required
def detalle_unidad(request, unidad_id):
    unidad = get_object_or_404(Unidad, id=unidad_id)
    curso = unidad.curso
    preguntas = unidad.preguntas.all()

    # Revisar si ya completó la unidad (en DB)
    completada_db = UnidadCompletada.objects.filter(usuario=request.user, unidad=unidad).exists()
    
    # Variable para controlar si mostrar la corrección (se activa después del POST)
    mostrar_correccion = completada_db 

    if unidad.tipo_contenido == "FORM":
        if request.method == "POST" and not completada_db:
            
            # --- Lógica de Guardado de Respuestas (SIEMPRE se ejecuta al enviar) ---
            todas_respondidas = True
            for pregunta in preguntas:
                opcion_id = request.POST.get(f"pregunta_{pregunta.id}")
                if opcion_id:
                    opcion = get_object_or_404(Opcion, id=opcion_id, pregunta=pregunta)
                    # Guardar respuesta
                    RespuestaUsuario.objects.update_or_create(
                        usuario=request.user,
                        pregunta=pregunta,
                        defaults={"opcion": opcion, "correcta": opcion.es_correcta}
                    )
                else:
                    todas_respondidas = False
            
            if not todas_respondidas:
                 messages.error(request, "❌ Por favor, responde todas las preguntas.")
                 # No se marca como completada, pero se puede mostrar corrección parcial si quieres
            
            # Recalcular si 'todas_correctas' después de guardar las respuestas
            respuestas_guardadas = RespuestaUsuario.objects.filter(usuario=request.user, pregunta__unidad=unidad)
            
            # Solo consideramos que respondió todas si la cantidad de respuestas guardadas es igual a la cantidad de preguntas
            if len(respuestas_guardadas) == preguntas.count():
                todas_correctas = all(r.opcion.es_correcta for r in respuestas_guardadas)
                
                # --- Lógica de Marcado de Unidad (Solo si TODAS son correctas) ---
                if todas_correctas and not completada_db:
                    UnidadCompletada.objects.get_or_create(usuario=request.user, unidad=unidad)
                    progreso, _ = Progreso.objects.get_or_create(estudiante=request.user, curso=curso)
                    progreso.actualizar_progreso()
                    messages.success(request, "✅ ¡Has completado correctamente el cuestionario!")
                    mostrar_correccion = True # Se marca para mostrar inmediatamente
                elif not todas_correctas:
                    messages.warning(request, "⚠️ Respuestas enviadas. No has completado el cuestionario correctamente.")
                    
                # Si el usuario ha enviado respuestas, SIEMPRE mostramos la corrección.
                mostrar_correccion = True # ESTE ES EL CAMBIO CLAVE: Muestra corrección después del POST.

            # IMPORTANTE: NO redirigir. Continuar para renderizar el template.
            # (El código continúa hacia la parte GET del formulario)


        # GET o después del POST: traer respuestas y correctas
        respuestas_usuario = RespuestaUsuario.objects.filter(usuario=request.user, pregunta__unidad=unidad)
        respuestas_dict = {r.pregunta_id: r.opcion_id for r in respuestas_usuario}

        # Diccionario de opciones correctas por pregunta
        opciones_correctas = {preg.id: [op.id for op in preg.opciones.filter(es_correcta=True)] for preg in preguntas}

        return render(request, "unidad_cuestionario.html", {
            "unidad": unidad,
            "preguntas": preguntas,
            "respuestas_dict": respuestas_dict,
            "opciones_correctas": opciones_correctas,
            "mostrar_correccion": mostrar_correccion, # Usa la variable que se actualiza
            "completada": UnidadCompletada.objects.filter(usuario=request.user, unidad=unidad).exists(), # Revisa si se completó en la DB
        })

    # VIDEO / TEXT / JUEGO
    # ... (El resto de la vista sin cambios)
    return render(request, "detalle_unidad.html", {
        "unidad": unidad,
        "curso": curso,
        "completada": completada_db,
    })

@login_required
def marcar_unidad_completada(request, unidad_id):
    """
    Endpoint que marca una unidad como completada para el usuario actual.
    Se puede llamar por fetch() desde el frontend cuando el usuario 'despliega' o
    inicia la reproducción del contenido.
    Devuelve JSON {'ok': True}.
    """
    unidad = get_object_or_404(Unidad, id=unidad_id)
    curso = unidad.curso

    
    creada = False
    obj, creada = UnidadCompletada.objects.get_or_create(
        usuario=request.user,
        unidad=unidad
    )

    
    if creada:
        request.user.puntos += 1
        request.user.puntos_totales += 1
        request.user.save()

   
    progreso, _ = Progreso.objects.get_or_create(estudiante=request.user, curso=curso)
    progreso.actualizar_progreso()

    return JsonResponse({"ok": True})


@login_required
def crear_curso(request):
    if request.method == 'POST':
        form = CursoForm(request.POST, request.FILES)
        if form.is_valid():
            curso = form.save(commit=False)
            curso.profesor = request.user
            curso.save()
            Unidad.objects.create(curso=curso, titulo="Formulario", tipo_contenido='FORM')
            Unidad.objects.create(curso=curso, titulo="Video", tipo_contenido='VIDEO')
            Unidad.objects.create(curso=curso, titulo="Juego", tipo_contenido='JUEGO')
            Unidad.objects.create(curso=curso, titulo="Texto", tipo_contenido='TEXT')
            messages.success(request, f"Curso '{curso.titulo}' creado con sus unidades base.")
            return redirect('configurar_curso', curso.id)
    else:
        form = CursoForm()
    return render(request, 'crear_curso.html', {'form': form})


@login_required
def configurar_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    
    unidad_form, _ = Unidad.objects.get_or_create(
        curso=curso, tipo_contenido='FORM', defaults={'titulo': 'Unidad 1: Cuestionario'}
    )
    unidad_video, _ = Unidad.objects.get_or_create(
        curso=curso, tipo_contenido='VIDEO', defaults={'titulo': 'Unidad 2: Video'}
    )
    unidad_juego, _ = Unidad.objects.get_or_create(
        curso=curso, tipo_contenido='JUEGO', defaults={'titulo': 'Unidad 3: Juego'}
    )
    unidad_texto, _ = Unidad.objects.get_or_create(
        curso=curso, tipo_contenido='TEXT', defaults={'titulo': 'Unidad 4: Texto'}
    )

    if request.method == 'POST':
       
        unidad_form.titulo = request.POST.get('titulo_form', unidad_form.titulo)
        unidad_form.descripcion = request.POST.get('descripcion_form', unidad_form.descripcion)
        unidad_form.save()

      
        Pregunta.objects.filter(unidad=unidad_form).delete()

       
        for i in range(1, 7):
            texto_pregunta = request.POST.get(f'pregunta_{i}', '').strip()
            if not texto_pregunta:
                continue

            pregunta = Pregunta.objects.create(unidad=unidad_form, texto=texto_pregunta)

            for j in range(1, 4):
                texto_opcion = request.POST.get(f'opcion_{i}_{j}', '').strip()
                if texto_opcion:
                    es_correcta = (request.POST.get(f'correcta_{i}') == str(j))
                    Opcion.objects.create(
                        pregunta=pregunta,
                        texto=texto_opcion,
                        es_correcta=es_correcta
                    )

        
        unidad_video.titulo = request.POST.get('titulo_video', unidad_video.titulo)
        unidad_video.descripcion = request.POST.get('descripcion_video', unidad_video.descripcion)

        
        if 'video_archivo' in request.FILES:
            unidad_video.video = request.FILES['video_archivo']

        
        if request.POST.get('video_url'):
            unidad_video.video_url = request.POST.get('video_url')

        unidad_video.save()

        
        unidad_juego.titulo = request.POST.get('titulo_juego', unidad_juego.titulo)
        unidad_juego.descripcion = request.POST.get('descripcion_juego', unidad_juego.descripcion)

        if 'juego_archivo' in request.FILES:
            unidad_juego.juego_archivo = request.FILES['juego_archivo']

        if request.POST.get('juego_url'):
            unidad_juego.juego_url = request.POST.get('juego_url')

        unidad_juego.save()

        
        unidad_texto.titulo = request.POST.get('titulo_texto', unidad_texto.titulo)
        unidad_texto.descripcion = request.POST.get('texto_contenido', unidad_texto.descripcion)
        unidad_texto.save()

        messages.success(request, "✅ El curso se configuró correctamente con todas las unidades.")
        return redirect('configurar_curso', curso.id)

    context = {
        'curso': curso,
        'unidad_form': unidad_form,
        'unidad_video': unidad_video,
        'unidad_juego': unidad_juego,
        'unidad_texto': unidad_texto,
    }
    return render(request, 'configurar_curso.html', context)


@login_required
def supervisar_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.user.role != 'profesor':
        messages.error(request, "Solo los profesores pueden supervisar cursos.")
        return redirect('catalogo')
    CursoProfesor.objects.get_or_create(curso=curso, profesor=request.user)
    messages.success(request, f"Ahora estás supervisando el curso '{curso.titulo}'.")
    return redirect('catalogo')


@login_required
def lista_estudiantes_profesor(request):
    if request.user.role != 'profesor':
        messages.error(request, "Solo los profesores pueden acceder a esta vista.")
        return redirect('inicio')

    cursos_supervisados = CursoProfesor.objects.filter(profesor=request.user).values_list('curso_id', flat=True)
    cursos = Curso.objects.filter(id__in=cursos_supervisados)
    datos_cursos = []

    for curso in cursos:
        inscripciones = Inscripcion.objects.filter(curso=curso).select_related('estudiante')
        estudiantes = []
        for inscripcion in inscripciones:
            estudiante = inscripcion.estudiante
            unidades_totales = curso.unidades.count()
            completadas = UnidadCompletada.objects.filter(usuario=estudiante, unidad__curso=curso).count()
            progreso = (completadas / unidades_totales * 100) if unidades_totales > 0 else 0
            estudiantes.append({
                'nombre': estudiante.username,
                'progreso': round(progreso, 1),
                'completadas': completadas,
                'totales': unidades_totales,
            })
        datos_cursos.append({'curso': curso, 'estudiantes': estudiantes})

    return render(request, 'profesor_estudiantes.html', {'datos_cursos': datos_cursos})
@login_required
def mis_cursos_profesor(request):
    if request.user.role != "profesor":
        messages.error(request, "Solo los profesores pueden ver esta sección.")
        return redirect("inicio")

    cursos = Curso.objects.filter(profesor=request.user)
    datos_cursos = []

    for curso in cursos:
        inscripciones = Inscripcion.objects.filter(curso=curso).select_related("estudiante")
        estudiantes = []
        for inscripcion in inscripciones:
            estudiante = inscripcion.estudiante
            total_unidades = curso.unidades.count()
            completadas = UnidadCompletada.objects.filter(
                usuario=estudiante, unidad__curso=curso
            ).count()
            progreso = int((completadas / total_unidades * 100)) if total_unidades > 0 else 0
            estudiantes.append({
                "nombre": estudiante.username,
                "progreso": progreso,
                "completadas": completadas,
                "totales": total_unidades,
            })
        datos_cursos.append({
            "curso": curso,
            "estudiantes": estudiantes,
        })

    return render(request, "mis_cursos_profesor.html", {"datos_cursos": datos_cursos})


@login_required
def tienda(request):
    
    if request.user.role != "estudiante":
        messages.error(request, "Solo los estudiantes pueden usar la tienda.")
        return redirect("inicio")

    items = ItemTienda.objects.all()
    inventario_qs = Inventario.objects.filter(usuario=request.user).select_related('item')
    
    items_comprados = list(inventario_qs.values_list("item_id", flat=True))

    return render(request, "tienda.html", {
        "items": items,
        "items_comprados": items_comprados,
        "inventario": inventario_qs,
        "usuario": request.user,
    })


@login_required
def comprar_item(request, item_id):
    
    if request.user.role != "estudiante":
        messages.error(request, "Solo los estudiantes pueden comprar objetos.")
        return redirect("tienda")

    item = get_object_or_404(ItemTienda, id=item_id)
    user = request.user

    if user.puntos < item.precio:
        messages.error(request, "No tienes suficientes puntos.")
        return redirect("tienda")

    
    user.puntos -= item.precio
    user.save()

    Inventario.objects.get_or_create(usuario=user, item=item)

    messages.success(request, f"¡Compraste {item.nombre}! 🎉")
    return redirect("tienda")


@login_required
def equipar_item(request, item_id):
    
    if request.user.role != "estudiante":
        messages.error(request, "Solo los estudiantes pueden equipar objetos.")
        return redirect("tienda")

    item = get_object_or_404(ItemTienda, id=item_id)
    user = request.user

    try:
        inv = Inventario.objects.get(usuario=user, item=item)
    except Inventario.DoesNotExist:
        messages.error(request, "Primero debes comprar este objeto.")
        return redirect("tienda")

    
    Inventario.objects.filter(usuario=user, item__tipo=item.tipo).update(equipado=False)
    inv.equipado = True
    inv.save()

    messages.success(request, f"{item.nombre} equipado ✔")
    return redirect("tienda")

@login_required
def enviar_correo_estudiantes(request):
    curso_id = request.POST.get('curso_id')
    curso = get_object_or_404(Curso, id=curso_id, profesor=request.user)
    correos = curso.inscripcion_set.values_list('estudiante__email', flat=True)
    mensaje = request.POST.get('mensaje', '')
    asunto = request.POST.get('asunto', '')

    if correos and mensaje:
        send_mail(
            asunto,
            mensaje,
            request.user.email,
            list(correos),
            fail_silently=False
        )

    return redirect('notificacion')

@login_required
def notificacion(request):
    cursos = Curso.objects.filter(profesor=request.user).filter(inscripcion__isnull=False).distinct()
    return render(request, 'notificacion.html', {'cursos': cursos})

def recursos(request):
    return render(request, 'recursos.html')


def nosotros(request):
    return render(request, 'nosotros.html')

@login_required
def datos_cuenta(request):
   
    icono_equipado = getattr(request.user, 'icono_url', None)  
    return render(request, 'datos_cuenta.html', {'icono_equipado': icono_equipado})