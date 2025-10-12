from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='estudiante')

    def __str__(self):
        return self.username
    

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


class Inscripcion(models.Model):
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'estudiante'}
    )
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
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
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='unidades')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.curso.titulo} - {self.titulo}"


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
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'unidad')