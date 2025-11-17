from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid
from django.core.exceptions import ValidationError
from django.utils.html import format_html


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
    )

    email = models.EmailField(unique=True)  

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='estudiante')
    puntos = models.IntegerField(default=0)
    puntos_totales = models.IntegerField(default=0)
    codigo_profesor = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.role == 'profesor' and not self.codigo_profesor:
            self.codigo_profesor = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"
    ROLE_CHOICES = (
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
    )

  
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='estudiante')

    
    puntos = models.IntegerField(default=0)
    puntos_totales = models.IntegerField(default=0)

    
    codigo_profesor = models.CharField(max_length=10, unique=True, null=True, blank=True)


    def save(self, *args, **kwargs):
        
        if self.role == 'profesor' and not self.codigo_profesor:
            self.codigo_profesor = str(uuid.uuid4())[:8].upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Curso(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    es_gratuito = models.BooleanField(default=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    profesor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'profesor'}
    )
    imagen = models.ImageField(upload_to='cursos/', null=True, blank=True)

    def __str__(self):
        return self.titulo


class CursoProfesor(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='supervisores')
    profesor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'profesor'}
    )
    fecha_asociacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('curso', 'profesor')

    def __str__(self):
        return f"{self.profesor.username} supervisa {self.curso.titulo}"


class Inscripcion(models.Model):
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'estudiante'}
    )
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    profesor_asignado = models.ForeignKey(   
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estudiantes_asignados',
        limit_choices_to={'role': 'profesor'}
    )
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.profesor_asignado:
            return f"{self.estudiante.username} -> {self.curso.titulo} ({self.profesor_asignado.username})"
        return f"{self.estudiante.username} -> {self.curso.titulo}"


class Carrito(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    cursos = models.ManyToManyField(Curso, blank=True)

    def total(self):
        return sum(c.precio for c in self.cursos.all() if c.precio)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"



class Modulo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='modulos')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.curso.titulo} - {self.titulo}"


class Unidad(models.Model):
    TIPO_CONTENIDO_CHOICES = (
        ('VIDEO', 'Video (Contenido principal)'),
        ('FORM', 'Formulario / Cuestionario'),
        ('TEXT', 'Texto (Contenido de lectura)'),
        ('JUEGO', 'Juego interactivo'),
    )

    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='unidades')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo_contenido = models.CharField(max_length=5, choices=TIPO_CONTENIDO_CHOICES, default='TEXT')

    video = models.FileField(upload_to='videos/', blank=True, null=True) 
    juego_url = models.URLField(max_length=300, blank=True, null=True, verbose_name="URL del juego externo (si es JUEGO)")
    juego_archivo = models.FileField(upload_to='juegos/', blank=True, null=True, verbose_name="Archivo ZIP/HTML del juego (si es JUEGO)")

    
    contenido_texto = models.TextField(blank=True, null=True, verbose_name="Contenido textual (si es TEXT)")

    def __str__(self):
        return f"{self.curso.titulo} - {self.titulo}"

    def obtener_url_juego(self):
        if self.juego_url:
            return self.juego_url
        elif self.juego_archivo and hasattr(self.juego_archivo, 'url'):
            return self.juego_archivo.url
        return None
    

class Pregunta(models.Model):
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE, related_name='preguntas')
    texto = models.CharField(max_length=255)

    def __str__(self):
        return self.texto


class Opcion(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='opciones')
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)

    def __str__(self):
        return self.texto


class RespuestaUsuario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    opcion = models.ForeignKey(Opcion, on_delete=models.CASCADE)
    correcta = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'pregunta')

    def save(self, *args, **kwargs):
        self.correcta = self.opcion.es_correcta
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.username} → {self.pregunta.texto} ({'✔' if self.correcta else '✖'})"



class UnidadCompletada(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    unidad = models.ForeignKey('Unidad', on_delete=models.CASCADE)
    completado = models.BooleanField(default=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'unidad')

    def __str__(self):
        return f"{self.usuario.username} completó {self.unidad.titulo}"

class Progreso(models.Model):
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'estudiante'})
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='progresos')
    unidades_completadas = models.IntegerField(default=0)
    total_unidades = models.IntegerField(default=0)
    actualizado = models.DateTimeField(auto_now=True)

    @property
    def porcentaje(self):
        if self.total_unidades == 0:
            return 0
        return int((self.unidades_completadas / self.total_unidades) * 100)

    def __str__(self):
        return f"{self.estudiante.username} - {self.curso.titulo}: {self.porcentaje}%"

    def actualizar_progreso(self):
        self.total_unidades = self.curso.unidades.count()
        self.unidades_completadas = UnidadCompletada.objects.filter(
            usuario=self.estudiante,
            unidad__curso=self.curso
        ).count()
        self.save()




class Pago(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    orden = models.CharField(max_length=100)
    monto = models.IntegerField()
    codigo_autorizacion = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago {self.orden} - {self.usuario.username}"


def validar_imagen_o_gif(file):
    valid_mimetypes = ['image/png', 'image/jpeg', 'image/gif']
    if file.content_type not in valid_mimetypes:
        raise ValidationError('Archivo no válido. Solo se permiten PNG, JPG o GIF.')
    
    
class ItemTienda(models.Model):
    TIPO_CHOICES = (
        ('BORDE', 'Borde de foto'),
        ('ICONO', 'Icono de perfil'),
        ('FONDO', 'Fondo de perfil'),
        ('GIF', 'GIF animado'),
    )

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.IntegerField(default=1)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    archivo = models.FileField(
        upload_to="tienda_items/",
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.nombre} (${self.precio})"

    def miniatura(self):
        if self.archivo:  
            return format_html('<img src="{}" width="100" style="object-fit:contain;" />', self.archivo.url)
        return "-"
    miniatura.short_description = "Vista previa"


class Inventario(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inventario"
    )
    item = models.ForeignKey(ItemTienda, on_delete=models.CASCADE)
    equipado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('usuario', 'item')

    def __str__(self):
        return f"{self.usuario.username} tiene {self.item.nombre}"