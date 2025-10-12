from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('admin/', admin.site.urls),
    path('inicio/', views.inicio, name='inicio'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path("catalogo/", views.catalogo, name="catalogo"),
    path("mis-cursos/", views.mis_cursos, name="mis_cursos"),
    path("inscribirse/<int:curso_id>/", views.inscribirse, name="inscribirse"),
    path('agregar/<int:curso_id>/', views.agregar_curso, name='agregar_curso'),
    path('carrito/', views.carrito, name='carrito'),
    path('comprar/', views.comprar_carrito, name='comprar_carrito'),

    path('curso/<int:curso_id>/', views.detalle_curso, name='detalle_curso'),
    path('unidad/<int:unidad_id>/responder/', views.responder_unidad, name='responder_unidad'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

