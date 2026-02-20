from django.shortcuts import render , redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from firebase_admin import firestore, auth
from config.firebase_connection import initialize_firebase
from functools import wraps
import requests
import os

#Inicializar la base de datos con firestore.
db = initialize_firebase()

def registro_usuario(request):
    mesaje = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            #Vamos a crear en fire base auth
            user = auth.create_user(
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

# --- Logica para el inicio de sesion

#Decorador de seguridad
def login_required_firebase(view_func):
    #este decorador personalisado va a proteger nuestras vistas
    #si el ususario no ha iniciado secion
    # si el UID no existe, lo va a enviar a iniciar sesion

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'uid' not in request.session:
            messages.warning(request, "Warning, no has iniciado secion")
            return redirect('login')
        return view_func(request, *args , **kwargs)
    return _wrapped_view

#Logica ppara solicirñe a google la validacion

def iniciar_sesion(request):
    #si ya esta loggeado. lo redirijo al deshboard

    if 'uid' in request.session:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        api_key = os.getenv('FIREBASE_WEB_API_KEY')

        #eNPOINT OFICIAL DE GOOGLE
        url =f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload={
            "email": email,
            "password" : password,
            "returnSecureToken" : True
        }

        try:
            #peticion http servicio de autenticacion google
            response = requests.post(url, json=payload)
            data = response.json()

            if response.status_code == 200:
                #Todo fue bien
                request.session['uid']= data['localId']
                request.session['email'] = data['email']
                request.session['idToken'] = data['idToken']
                messages.success(request, f"✔️Acceso corecto al sistema")
                return redirect('dashboard')
            else:
                #error: Analizar el error
                error_message = data.get('error',{}).get('message', 'UNKNOWN_ERROR')

                errores_comunes = {
                    'INVALID_LOGIN_CREDENTIALS': 'La contraseña es incorrecta o el correo no es válido.',
                    'EMAIL_NOT_FOUND': 'Este correo no está registrado en el sistema.',
                    'USER_DISABLED': 'Esta cuenta ha sido inhabilitada por el administrador.',
                    'TOO_MANY_ATTEMPTS_TRY_LATER': 'Demasiados intentos fallidos. Espere unos minutos.'
                }

                mensaje_usuario = errores_comunes.get(error_message, "Error de autenticacion")
                messages.error(request, mensaje_usuario)
            
        except requests.exceptions.RequestException as e:
            messages.error(request, "Error de conexion con el servidor")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
    
    return render(request, 'login.html')

def cerrar_secion(request):
    #limpiar la cecion y luego se redirije
    request.session.flush()
    messages.info(request,"Has cerrado secion correctamente")
    return redirect('login')
