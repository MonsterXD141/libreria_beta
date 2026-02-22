from django.urls import path
#para poder importar todas las funciones de views
from . import views

urlpatterns = [
    # Asociar la funcion a la vista con url /registro/
    path('registro/',views.registro_usuario, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('libros/', views.listar_recerva, name='listar_recerva'),
    path('libros/reserva/', views.crear_reserva, name='crear_recerva'),
    path('libros/eliminar/<str:reserva_id>/', views.eliminar_reserva, name='eliminar_reserva'),
    path('libros/editar/<str:reserva_id>/', views.editar_recerva, name='editar_reserva')
]