from django.urls import path
from . import views

urlpatterns =[
    #Asociar la función a la vista con url /registro/
    path('registro/',views.registro_usuario, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('dashboard/', views.dashboard, name='dashboard')
    
]
