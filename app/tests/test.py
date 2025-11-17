from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from app.models import (
    CustomUser, Curso, Inscripcion, Carrito, Modulo, Unidad, 
    Pregunta, Opcion, RespuestaUsuario, UnidadCompletada, Progreso, 
    ItemTienda, Inventario, CursoProfesor
)

User = get_user_model()

class CustomUserModelTests(TestCase):
    def test_codigo_profesor_generado_en_save(self):
        profesor = User.objects.create(username='teacher1', email='t1@example.com', role='profesor')
        self.assertIsNotNone(profesor.codigo_profesor)
        self.assertEqual(len(profesor.codigo_profesor), 8)

    def test_estudiante_no_genera_codigo(self):
        estudiante = User.objects.create(username='student1', email='s1@example.com', role='estudiante')
        self.assertIsNone(estudiante.codigo_profesor)

    def test_codigo_profesor_no_cambia_al_actualizar(self):
        profesor = User.objects.create(username='teacher2', email='t2@example.com', role='profesor')
        original_code = profesor.codigo_profesor
        profesor.puntos = 100
        profesor.save()
        self.assertEqual(profesor.codigo_profesor, original_code)

    def test_str_representation(self):
        profesor = User.objects.create(username='test_profe', email='tp@e.com', role='profesor')
        self.assertEqual(str(profesor), "test_profe (profesor)")

class CursoAndInscripcionTests(TestCase):
    def setUp(self):
        self.profesor_principal = User.objects.create_user(username='prof1', email='p1@e.com', role='profesor')
        self.profesor_aux = User.objects.create_user(username='prof_aux', email='pa@e.com', role='profesor')
        self.estudiante = User.objects.create_user(username='est1', email='s1@e.com', role='estudiante')
        self.curso = Curso.objects.create(titulo='Programación con Python', descripcion='D', profesor=self.profesor_principal)

    def test_curso_creacion_exitosa(self):
        self.assertEqual(self.curso.profesor, self.profesor_principal)
        self.assertEqual(self.curso.titulo, 'Programación con Python')

    def test_curso_profesor_unique_together(self):
        CursoProfesor.objects.create(curso=self.curso, profesor=self.profesor_aux)
        with self.assertRaises(IntegrityError):
            CursoProfesor.objects.create(curso=self.curso, profesor=self.profesor_aux)

    def test_inscripcion_con_profesor_asignado(self):
        inscripcion = Inscripcion.objects.create(estudiante=self.estudiante, curso=self.curso, profesor_asignado=self.profesor_aux)
        self.assertIsNotNone(inscripcion.profesor_asignado)
        self.assertEqual(inscripcion.profesor_asignado, self.profesor_aux)

class CarritoModelTests(TestCase):
    def setUp(self):
        profesor = User.objects.create_user(username='p', email='p@e.com', role='profesor')
        usuario = User.objects.create_user(username='u', email='u@e.com')
        self.carrito = Carrito.objects.create(usuario=usuario)
        self.curso_pagado_10 = Curso.objects.create(titulo='C1', descripcion='D', profesor=profesor, es_gratuito=False, precio=10.00)
        self.curso_pagado_20_50 = Curso.objects.create(titulo='C2', descripcion='D', profesor=profesor, es_gratuito=False, precio=20.50)
        self.curso_gratuito = Curso.objects.create(titulo='C3', descripcion='D', profesor=profesor, es_gratuito=True, precio=None)

    def test_total_calculo_cursos_pagados(self):
        self.carrito.cursos.add(self.curso_pagado_10, self.curso_pagado_20_50)
        self.assertEqual(self.carrito.total(), 30.50)

    def test_total_ignora_cursos_gratuitos(self):
        self.carrito.cursos.add(self.curso_pagado_10, self.curso_gratuito)
        self.assertEqual(self.carrito.total(), 10.00)

class RespuestaUsuarioModelTests(TestCase):
    def setUp(self):
        self.estudiante = User.objects.create_user(username='s', email='s@e.com', role='estudiante')
        profesor = User.objects.create_user(username='p', email='p@e.com', role='profesor')
        self.curso = Curso.objects.create(titulo='C', descripcion='D', profesor=profesor)
        self.unidad = Unidad.objects.create(curso=self.curso, titulo='U')
        self.pregunta = Pregunta.objects.create(unidad=self.unidad, texto='Q1')
        self.opcion_correcta = Opcion.objects.create(pregunta=self.pregunta, texto='A', es_correcta=True)
        self.opcion_incorrecta = Opcion.objects.create(pregunta=self.pregunta, texto='B', es_correcta=False)

    def test_respuesta_correcta_auto_set(self):
        respuesta = RespuestaUsuario.objects.create(usuario=self.estudiante, pregunta=self.pregunta, opcion=self.opcion_correcta)
        self.assertTrue(respuesta.correcta)

    def test_respuesta_incorrecta_auto_set(self):
        respuesta = RespuestaUsuario.objects.create(usuario=self.estudiante, pregunta=self.pregunta, opcion=self.opcion_incorrecta)
        self.assertFalse(respuesta.correcta)

    def test_unica_respuesta_por_pregunta(self):
        RespuestaUsuario.objects.create(usuario=self.estudiante, pregunta=self.pregunta, opcion=self.opcion_correcta)
        with self.assertRaises(IntegrityError):
            RespuestaUsuario.objects.create(usuario=self.estudiante, pregunta=self.pregunta, opcion=self.opcion_incorrecta)

class ProgresoModelTests(TestCase):
    def setUp(self):
        self.profesor = User.objects.create_user(username='p', email='p@e.com', role='profesor')
        self.estudiante = User.objects.create_user(username='s', email='s@e.com', role='estudiante')
        self.curso = Curso.objects.create(titulo='C1', descripcion='D', profesor=self.profesor)
        self.unidad1 = Unidad.objects.create(curso=self.curso, titulo='U1')
        self.unidad2 = Unidad.objects.create(curso=self.curso, titulo='U2')
        self.unidad3 = Unidad.objects.create(curso=self.curso, titulo='U3')
        self.progreso = Progreso.objects.create(estudiante=self.estudiante, curso=self.curso)

    def test_propiedad_porcentaje(self):
        self.progreso.total_unidades = 5
        self.progreso.unidades_completadas = 2
        self.assertEqual(self.progreso.porcentaje, 40)

    def test_porcentaje_cero_sin_unidades(self):
        self.progreso.total_unidades = 0
        self.progreso.unidades_completadas = 0
        self.assertEqual(self.progreso.porcentaje, 0)
    
    def test_actualizar_progreso_correcto(self):
        UnidadCompletada.objects.create(usuario=self.estudiante, unidad=self.unidad1)
        UnidadCompletada.objects.create(usuario=self.estudiante, unidad=self.unidad3)
        self.progreso.actualizar_progreso()
        self.assertEqual(self.progreso.total_unidades, 3)
        self.assertEqual(self.progreso.unidades_completadas, 2)
        self.assertEqual(self.progreso.porcentaje, 66)

class UnidadModelTests(TestCase):
    def setUp(self):
        profesor = User.objects.create_user(username='p', email='p@e.com', role='profesor')
        self.curso = Curso.objects.create(titulo='C', descripcion='D', profesor=profesor)
        
    def test_obtener_url_juego_desde_url(self):
        unidad = Unidad.objects.create(curso=self.curso, titulo='U1', tipo_contenido='JUEGO', juego_url='http://juego.com/game')
        self.assertEqual(unidad.obtener_url_juego(), 'http://juego.com/game')

    def test_obtener_url_juego_desde_archivo(self):
        class MockFile:
            @property
            def url(self):
                return '/media/juegos/archivo.zip'
        
        unidad = Unidad.objects.create(curso=self.curso, titulo='U2', tipo_contenido='JUEGO')
        unidad.juego_archivo = MockFile()
        self.assertEqual(unidad.obtener_url_juego(), '/media/juegos/archivo.zip')

    def test_obtener_url_juego_retorna_none(self):
        unidad = Unidad.objects.create(curso=self.curso, titulo='U3', tipo_contenido='JUEGO')
        self.assertIsNone(unidad.obtener_url_juego())
