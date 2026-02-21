from django.urls import path
from . import views

urlpatterns =[
    #Asociar la función a la vista con url /registro/
    path('registro/',views.registro_usuario, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('libros/', views.listar_recerva, name='listar_recerva'),
    path('libros/reserva/', views.crear_reserva, name='crear_recerva'),
    path('libros/eliminar/<str:recerba_id>/', views.eliminar_reserva, name='eliminar_recerva'),
    path('libros/editar/<str:recerba_id>/', views.editar_recerva, name='editar_recerva')
]
