from django.shortcuts import render , redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from firebase_admin import firestore, auth
from config.firebase_connection import initialize_firebase
from functools import wraps
import requests
import os

#Inicializar la base de datos con firestore
db = initialize_firebase()

def registro_usuario(request):
    mesaje = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            #Vamos a crear en fire base auth
            user = auth.create.user(
                email = email,
                password = password
            )

            #vamos a crear en firestore
            db.collection('perfiles').document(user.uid).set({
                'email' :email,
                'uid' : user.uid,
                'rol' : 'aprensiz',
                'fecha_registro': firestore.SERVER_TIMESTAMP
            })

            mesaje= f"Usuario registrado corectamente con USD: {user.uid}"
        except Exception as e:
            mesaje= f"😱 Error_: {e}"
            
    return render(request, 'registro.html' , {'mesaje' : mesaje})