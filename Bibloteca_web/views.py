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

def cerrar_sesion(request):
    #limpiar la cecion y luego se redirije
    request.session.flush()
    messages.info(request,"Has cerrado secion correctamente")
    return redirect('login')

@login_required_firebase
def dashboard(request):
    """
    panel principal este. solo es accesible si el decorador lo permite
    Revuperar los datos de firestore
    """

    uid = request.session.get('uid')
    datos_usuario = {}
    try:
        #consulta a firestore usando nuestro SDK
        doc_ref = db.collection('perfiles').document(uid)
        doc = doc_ref.get()
        
        if doc.exists:
            datos_usuario = doc.to_dict()
        else:
            # si entra en el auth pero no tiene un perfil en firestore, manejo el caso
            datos_usuario={
                'email' : request.session.get('email'),
                'uid' : request.session.get('uid'),
                'rol' : 'usuario',
                'fecha_registro' : firestore.SERVER_TIMESTAMP,
            }
    except Exception as e:
        messages.error(request, f"Error al cargar los datos de la BD: {e}")
    return render(request, 'dashboard.html', {'datos': datos_usuario})


@login_required_firebase
def listar_recerva(request):
    """
    READ: Recuperar las recervas del usuario
    """

    uid = requests.sessio.get('uid')
    recervas =[]

    try:
        #vamos a filtrar las recervas del usuario

        docs = db.collection('recervas').where('usuario_id', '==',uid).stream()
        for doc in docs:
            recerva = doc.to_dict()
            recerva['id'] = doc.id
            recervas.append[recervas]
    except Exception as e:
        messages.error(request, f"Hubo un error al obtener las recervas {e}")
    return render(request, 'libros/listar.html', {'recervas':recervas})


@login_required_firebase
def crear_reserva(request):
    """
    CREATE: recibe los datos desde el formulario y se almacenan
    """

    if (request.method == 'POST'):
        titulo = request.POST.get('titulo')
        fecha_recerva = request.POST.get('fecha_recerva')
        uid = request.POST.get('uid')

        try:
            db.collection('recervas').add({
                'titulo' : titulo,
                'fecha_recerva' : fecha_recerva,
                'usuario_id' : uid ,
                'fecha_creacion' : firestore.SERVER_TIMESTAMP
            })
            messages.succes(request, "recerva creada con exito")
            return redirect('lista_recerva')
        except Exception as e:
            messages.error(request, f"Error al crear la reserva {e}")
    return render(request, 'libros/form.html')

@login_required_firebase
def eliminar_reserva(request, recerva_id):
    """
    DELETE: Elimina el documento especifico por id
    """

    try:
        db.collection('recervas').document(recerva_id).delete()
        messages.success(request, "recerva eliminada.")
    except Exception as e:
        messages.error(request,f"Error al eliminar: {e}")
    return redirect('listar_recervas')