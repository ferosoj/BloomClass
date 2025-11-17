import pytest
from django.contrib.auth import get_user_model
# Importamos todos los modelos que vamos a necesitar para las fixtures
from app.models import Curso, Inscripcion, Unidad, Pregunta, Opcion, Modulo 

# --- 1. Fixtures de Datos y Usuario Estudiante ---

@pytest.fixture
def estudiante_data():
    """Proporciona datos base para crear o loguear un CustomUser (Estudiante)."""
    return {
        'username': 'testestudiante',
        'email': 'estudiante@example.com',
        'password': 'strongpassword123', 
        'role': 'estudiante' # Aseguramos el rol para las pruebas de Inscripcion
    }

@pytest.fixture
def custom_user_creado(db, estudiante_data):
    """Crea y devuelve una instancia de CustomUser con rol 'estudiante'."""
    CustomUser = get_user_model()
    # Usamos create_user para que la contraseña se hashee correctamente
    user = CustomUser.objects.create_user(**estudiante_data)
    user.role = 'estudiante' # Aseguramos el rol en el objeto
    user.save()
    return user

@pytest.fixture
def auth_client(client, custom_user_creado):
    """Devuelve un Django Test Client con el custom_user_creado (estudiante) logueado."""
    # La contraseña debe coincidir con la de 'estudiante_data'
    client.login(username=custom_user_creado.username, password='strongpassword123')
    return client

# --- 2. Fixtures de Usuario Profesor y Curso ---

@pytest.fixture
def profesor_creado(db):
    """Crea un usuario con rol 'profesor', requerido por el modelo Curso."""
    CustomUser = get_user_model()
    return CustomUser.objects.create_user(
        username='profesor_test',
        email='profesor@test.com',
        password='strongpassword123',
        role='profesor'
    )

@pytest.fixture
def curso_inicial(db, profesor_creado):
    """Crea y devuelve una instancia del modelo Curso, usando el profesor."""
    # Usamos el campo 'titulo' de tu modelo Curso
    return Curso.objects.create(
        titulo="Curso de Fundamentos",
        descripcion="Descripción de prueba para el curso.",
        es_gratuito=False,
        precio=50.00,
        profesor=profesor_creado
    )

@pytest.fixture
def inscripcion_completa(db, custom_user_creado, curso_inicial):
    """Crea una Inscripcion para el estudiante en el curso, simulando un pago exitoso."""
    return Inscripcion.objects.create(
        estudiante=custom_user_creado,
        curso=curso_inicial,
    )

# --- 3. Fixtures para la Estructura de Unidades y Formularios ---

@pytest.fixture
def unidad_inicial(db, curso_inicial):
    """Crea una Unidad de tipo FORMULARIO asociada al curso para pruebas de cuestionario."""
    # Nota: Tu modelo Unidad apunta directamente a Curso, sin FK a Modulo.
    return Unidad.objects.create(
        curso=curso_inicial,
        titulo="Cuestionario de Evaluación",
        tipo_contenido='FORM', # Esencial para la prueba de formularios
    )

@pytest.fixture
def pregunta_inicial(db, unidad_inicial):
    """Crea una Pregunta asociada a la Unidad."""
    return Pregunta.objects.create(
        unidad=unidad_inicial,
        texto="¿Qué framework de Python se usa en este proyecto?"
    )

@pytest.fixture
def opcion_correcta_inicial(db, pregunta_inicial):
    """Crea una Opción CORRECTA para la Pregunta."""
    return Opcion.objects.create(
        pregunta=pregunta_inicial,
        texto="Django",
        es_correcta=True
    )
    
@pytest.fixture
def opcion_incorrecta_inicial(db, pregunta_inicial):
    """Crea una Opción INCORRECTA para la Pregunta."""
    return Opcion.objects.create(
        pregunta=pregunta_inicial,
        texto="Flask",
        es_correcta=False
    )
