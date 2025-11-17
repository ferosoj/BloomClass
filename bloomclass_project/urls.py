from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

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
    path('carrito/eliminar/<int:curso_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/comprar/', views.comprar_carrito, name='comprar_carrito'),
    path('pago_webpay/', views.pago_webpay, name='pago_webpay'),
    path('confirmar_pago/', views.confirmar_pago, name='confirmar_pago'),
    path("historial_pagos/", views.historial_pagos, name="historial_pagos"),
    path('curso/<int:curso_id>/', views.detalle_curso, name='detalle_curso'),
    path('unidad/<int:unidad_id>/', views.detalle_unidad, name='detalle_unidad'),
    path('crear-curso/', views.crear_curso, name='crear_curso'),
    path('curso/<int:curso_id>/configurar/', views.configurar_curso, name='configurar_curso'),
    path('curso/<int:curso_id>/supervisar/', views.supervisar_curso, name='supervisar_curso'),
    path('profesor/estudiantes/', views.lista_estudiantes_profesor, name='lista_estudiantes_profesor'),
    path("mis-cursos-profesor/", views.mis_cursos_profesor, name="mis_cursos_profesor"),
    path('unidad/<int:unidad_id>/marcar-completada/', views.marcar_unidad_completada, name='marcar_unidad_completada'),
    path("tienda/", views.tienda, name="tienda"),
    path("tienda/comprar/<int:item_id>/", views.comprar_item, name="comprar_item"),
    path("tienda/equipar/<int:item_id>/", views.equipar_item, name="equipar_item"),
    path('password-reset/',auth_views.PasswordResetView.as_view(template_name="password_reset.html"),name="password_reset"),
    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"),name="password_reset_done"),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"),name="password_reset_confirm"),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"),name="password_reset_complete"),
    path('notificacion/', views.notificacion, name='notificacion'),
    path('enviar-correo/', views.enviar_correo_estudiantes, name='enviar_correo'),
    path('recursos/', views.recursos, name='recursos'), 
    path('nosotros/', views.nosotros, name='nosotros'),
    path('datos_cuenta/', views.datos_cuenta, name='datos_cuenta'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

