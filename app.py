"""
PROYECTO: PowerFull Club - Sistema de Gestión de Rollers
ARCHIVO: app.py
DESCRIPCIÓN: Controlador principal de Flask. Gestiona las rutas web (URLS)
             y conecta la interfaz de usuario con la lógica de datos.
AUTOR: Omar Castañeda
"""




#   SECCION: CONFIGURADOR DEL SERVIDOR   #
#Importa las librerías de Flask para gestionar las rutas y el protocolo de comunicación entre el 
#servidor y el navegador del usuario. Establece la conexión con el módulo logic.py, permitiendo 
#que la lógica de negocio y las operaciones de base de datos se integren al flujo principal de 
#la aplicación.

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime  
import logic
import os
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv




# ==========================================
# CONFIGURACIÓN DE SEGURIDAD Y NUBE
# ==========================================

# 1. ABRIMOS LA BÓVEDA (.env)
load_dotenv()

# 2. Configuramos Cloudinary sacando las llaves de la bóveda
cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.getenv("CLOUDINARY_API_KEY"), 
  api_secret = os.getenv("CLOUDINARY_API_SECRET") 
)





#   SECCION: MOTOR PRINCIPAL DE APLICACION   #
#Inicializa la instancia principal del framework, creando el objeto central que coordinará 
# todas las funciones del servidor. Define el contexto del sistema mediante la variable 
# global __name__, la cual permite a la aplicación localizar recursos, plantillas y archivos 
# estáticos dentro del directorio del proyecto.
app = Flask(__name__)





#    ACTIVADOR DE ALERTAS SEGURAS   #
#Esta función actúa como el sello de autenticidad de tu aplicación. Sirve para "firmar" y 
# cifrar la comunicación entre el servidor y el navegador, permitiendo que Flask use su 
# sistema de mensajes flash (las alertas que aparecen al registrar o borrar alumnos) de 
# forma segura, garantizando que nadie pueda alterar la información durante la sesión del 
# usuario.
app.secret_key = os.getenv("FLASK_SECRET_KEY")




#   RUTA DE ALMACENAMIENTO LOCAL SERVIDOR   #
#Establece la ruta del directorio local destinado al almacenamiento temporal o permanente de archivos 
# dentro del servidor. En el contexto actual de Cloudinary, esta línea se vuelve opcional o secundaria, 
# ya que el almacenamiento principal se ha desplazado de tu disco duro hacia la nube.
app.config['UPLOAD_FOLDER'] = 'static/uploads'








# --- ESTO VA JUSTO ANTES ---
CLAVE_PROFESOR = "Codigo777-profesor"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password_ingresada = request.form.get('password')
        if password_ingresada == CLAVE_PROFESOR:
            session['admin'] = True
            return redirect(url_for('home'))
        return "Contraseña incorrecta. <a href='/login'>Volver a intentar</a>"
    
    return '''
    <div style="
        display: flex; 
        justify-content: center; 
        align-items: center; 
        height: 100vh; 
        width: 100%;
        background: url('https://images.unsplash.com/photo-1547447134-cd3f5c716030?q=80&w=1964&auto=format&fit=crop') no-repeat center center fixed; 
        background-size: cover;
        font-family: 'Poppins', sans-serif;
        margin: 0;
    ">
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,255,255,0.1); z-index: 1;"></div>

        <div style="
            position: relative;
            z-index: 2;
            background: rgba(255, 255, 255, 0.85); 
            padding: 80px; 
            border-radius: 40px; 
            /* Quitamos la sombra negra y ponemos un resplandor de luz */
            box-shadow: 0 0 40px rgba(255, 255, 255, 0.5); 
            text-align: center; 
            width: 600px; 
            border: 1px solid rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(15px);
        ">
            <div style="font-size: 80px; margin-bottom: 20px;">🛼</div>
            <h1 style="color: #1a2a6c; margin-bottom: 10px; font-size: 3.5rem; font-weight: 900; letter-spacing: -2px; line-height: 1;">POWERFULL</h1>
            <p style="color: #333; margin-bottom: 50px; font-size: 1.4rem; font-weight: 500; text-transform: uppercase; letter-spacing: 2px;">Panel de Control Administrativo</p>
            
            <form method="post">
                <div style="margin-bottom: 35px; text-align: left;">
                    <label style="display: block; margin-bottom: 15px; color: #1a2a6c; font-weight: 700; font-size: 1rem; padding-left: 5px;">CONTRASEÑA MAESTRA</label>
                    <input type="password" name="password" placeholder="••••••••" required 
                           style="width: 100%; padding: 22px; border: 2px solid rgba(26, 42, 108, 0.2); border-radius: 15px; box-sizing: border-box; outline: none; font-size: 1.3rem; transition: 0.3s; background: rgba(255,255,255,0.8);">
                </div>
                
                <button type="submit" 
                        style="width: 100%; padding: 22px; background: linear-gradient(to right, #1a2a6c, #b21f1f, #fdbb2d); color: white; border: none; border-radius: 15px; font-size: 1.4rem; font-weight: 800; cursor: pointer; transition: 0.3s; text-transform: uppercase; letter-spacing: 1px;">
                    ACCEDER AL SISTEMA
                </button>
            </form>
            
            <div style="margin-top: 40px; padding-top: 25px; border-top: 1px solid rgba(0,0,0,0.1);">
                <p style="font-size: 0.9rem; color: #555; font-weight: 600;">🔒 SISTEMA DE SEGURIDAD ACTIVADO</p>
            </div>
        </div>
    </div>
    '''



@app.route('/logout')
def logout():
    session.pop('admin', None)  # Esto "borra" el brazalete VIP
    return redirect(url_for('login'))







#   INTEGRACION DE METRICAS TOTALES   #
#Actualiza el "menú de entrega" del servidor para que, además de los datos de pago, incluya el análisis 
# de asistencia y rendimiento grupal, permitiendo que el HTML pueda dibujar las tarjetas del panel del 
# profesor.
# En app.py
@app.route('/')
def home():
    # 🔒 EL CANDADO (Agrégalo aquí mismo)
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    # --- De aquí para abajo es tu código que ya funciona ---
    
    # 1. ESTA NO SE TOCA (Maneja los colores verde/rojo)
    alumnos_datos = logic.obtener_alumnos_con_estado_pago()
    
    # 2. ESTA ES LA QUE ARREGLAMOS (Trae la lista de pagos)
    lista_pagos = logic.obtener_ultimos_pagos() 
    
    # 3. ESTADÍSTICAS (Maneja las gráficas)
    stats = logic.obtener_estadisticas_profe()
    
    return render_template('index.html', 
                           alumnos=alumnos_datos, 
                           pagos=lista_pagos,
                           stats_profe=stats)





#   RECEPTOR DE NUEVOS ALUMNOS   #
#Implementa un punto de enlace (endpoint) de tipo POST diseñado para la captura y 
#serialización de datos provenientes del formulario de registro. Transforma las entradas 
#del usuario en un objeto de diccionario estructurado y activa la función de persistencia en 
#la capa de lógica antes de redirigir al usuario a la vista principal.
@app.route('/registrar', methods=['POST'])
def registrar():
    # 1. Recolectamos los datos de texto (Igual que antes, pero 'foto' empieza vacío)
    datos = {
        "nombre": request.form.get('nombre'),
        "cedula": request.form.get('cedula'),
        "whatsapp": request.form.get('whatsapp'),
        "fecha_nac": request.form.get('fecha_nac'),
        "sangre": request.form.get('sangre'),
        "eps": request.form.get('eps'),
        "emergencia_nombre": request.form.get('emergencia_nombre'),
        "parentesco": request.form.get('parentesco'),
        "emergencia_tel": request.form.get('emergencia_tel'),
        "foto": "" # Se llenará con la respuesta de Cloudinary
    }

    # 2. CAPTURAMOS EL ARCHIVO (Cámara o Galería)
    # Buscamos en 'request.files' en lugar de 'request.form'
    archivo_foto = request.files.get('foto')

    if archivo_foto and archivo_foto.filename != '':
        try:
            # Subimos el archivo directamente a Cloudinary usando tu configuración
            resultado = cloudinary.uploader.upload(
                archivo_foto,
                folder="rollers_powerfull", # Carpeta organizada en tu nube
                public_id=f"perfil_{datos['cedula']}" # Nombre único usando la cédula
            )
            # Guardamos la URL segura en el sobre de datos
            datos["foto"] = resultado.get('secure_url')
            print(f"✅ Foto de {datos['nombre']} subida exitosamente.")
        except Exception as e:
            print(f"❌ Error al subir a Cloudinary: {e}")
            # Si falla, el alumno se guarda sin foto (no se rompe la app)

    # 3. Mandamos el diccionario completo a la lógica (Tu código original)
    if datos["nombre"]:
        logic.guardar_alumno(datos) 
        flash("✅ ¡Patinador y foto guardados con éxito!", "success") 
    
    return redirect(url_for('home'))







#   BORRADO SEGURO DE REGISTROS   #
#Implementa un endpoint con parámetros dinámicos que captura el identificador único (ID) 
#del recurso para ejecutar una operación de borrado. Utiliza este identificador para 
#localizar el registro exacto en MongoDB a través de la capa de lógica, garantizando una e
#eliminación precisa y segura. Finalmente, restablece el estado de la interfaz mediante una 
#redirección para reflejar los cambios en tiempo real.
@app.route('/eliminar/<id_alumno>', methods=['POST'])
def eliminar(id_alumno):
    # 1. Usamos tu lógica que ya funciona
    exito = logic.borrar_alumno(id_alumno)
    
    # 2. En lugar de hacer redirect, respondemos con éxito para que el JS lo lea
    return jsonify({"success": True, "mensaje": "🗑️ Registro eliminado correctamente"})








#   CONTOR DE PRESNTISMO DIARIO   #
#Esta función actúa como un reloj checador digital. Su trabajo es detectar qué alumno llegó 
# al club, obtener automáticamente la fecha del día de hoy y enviar esa información a la 
# base de datos para que quede constancia de su asistencia, mostrando finalmente un mensaje 
# de confirmación en pantalla.
@app.route('/marcar_asistencia/<id_alumno>', methods=['POST'])
def marcar_asistencia(id_alumno):
    # 1. Capturamos la fecha actual
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    
    # 2. En lugar de intentar guardarlo aquí, llamamos a la función de logic.py
    # Le pasamos el ID y la Fecha
    logic.guardar_asistencia(id_alumno, fecha_hoy)
    
    # 3. Avisamos a David que todo salió bien
    flash(f"✅ Asistencia registrada para el {fecha_hoy}", "success")
    return redirect(url_for('home'))






#   LIMPIEZA DE ERRORES HISTORICOS   #
#Esta función actúa como un corrector de registros de entrada. Su propósito es localizar 
# una asistencia específica mediante su identificador y eliminarla permanentemente de la base 
# de datos, permitiendo así rectificar errores manuales o cancelaciones de clase en el historial 
# del club.
@app.route('/eliminar_asistencia/<id_asistencia>', methods=['POST'])
def eliminar_asistencia(id_asistencia):
    # Llamamos a la nueva función de la capa logic
    logic.borrar_asistencia(id_asistencia)
    
    flash("🗑️ Registro de asistencia eliminado", "danger")
    return redirect(url_for('historial'))





#   ARCHIVO DE VISITAS PASADAS   #
#Este bloque de código se encarga de organizar y mostrar el historial de visitas. Su función 
# es pedirle a la lógica del sistema que junte los nombres con sus fechas de asistencia para 
# presentarlos en una lista ordenada dentro de una nueva pantalla llamada "historial".
@app.route('/historial')
def historial():
    # 1. Le pedimos a logic que haga el cruce de datos (ID -> Nombre)
    reporte_asistencias = logic.obtener_historial_asistencias()
    
    # 2. Abrimos la nueva capa de código y le pasamos la lista de asistencias
    return render_template('historial.html', asistencias=reporte_asistencias)









#   PUENTE DE DATOS TEMPORAL PARA REGISTRO DEL HISTORIAL   #
#Este bloque funciona como el servidor de datos bajo demanda. Su tarea es estar a la escucha de 
# la petición del calendario, solicitar a la base de datos (a través de la lógica) la lista de 
# entrenamientos registrados y entregar esa información en un formato especial llamado JSON, 
# para que el calendario pueda "dibujar" cada evento en el día exacto.
@app.route('/obtener_eventos')
def obtener_eventos():
    # Le pedimos a la lógica que nos traiga los entrenamientos
    eventos = logic.listar_eventos_calendario()
    # Los devolvemos en formato JSON (el idioma que entiende el calendario)
    return jsonify(eventos)







@app.route('/api/calendario_eliminar/<id_asistencia>', methods=['POST'])
def ruta_eliminar_asistencia_calendario(id_asistencia):
    # Llama a la lógica destructora
    exito = logic.eliminar_asistencia(id_asistencia)
    # Responde con JSON65tybn 0o0o5
    return jsonify({"success": exito})







#    VISOR DE ASISTENCIAS TOTALES   #
#Este código es el organizador de la bitácora. Su trabajo es ir a la base de datos, buscar 
# todos los registros de quién vino y cuándo, y "traducirlos" para que aparezcan ordenados en
#  una tabla clara dentro de la pantalla de historial, permitiéndote ver el pasado del club sin 
# complicaciones.
@app.route('/registrar_pago/<id_alumno>') 
def registrar_pago(id_alumno):
    # Capturamos lo que viene después del signo '?' en la URL
    monto = request.args.get('monto')
    tipo = request.args.get('tipo')
    
    print(f"DEBUG: ¡Señal recibida! ID: {id_alumno}, Tipo: {tipo}, Monto: {monto}")
    
    if monto and tipo:
        logic.registrar_pago(id_alumno, monto, tipo)
        flash(f"✅ Pago de {tipo} registrado", "success")
    
    return redirect(url_for('home'))





#   GESTOR DE BORRADO CONTABLE   #
#Funciona como el mensajero de órdenes. Su tarea es recibir el identificador único del pago 
# que quieres quitar, llamar a la base de datos para que lo borre y avisarte con un mensaje 
# de color (flash) si la operación salió bien o si hubo algún problema, refrescando la lista 
# automáticamente.
@app.route('/eliminar_pago/<id_pago>')
def eliminar_pago(id_pago):
    # Intentamos borrar el pago usando la lógica
    if logic.borrar_pago(id_pago):
        flash("🗑️ Pago eliminado correctamente", "info")
    else:
        flash("❌ No se pudo eliminar el pago", "danger")
    
    # Después de borrarlo, volvemos a la página de inicio (o donde tengas la tabla)
    return redirect(url_for('home'))







#    GESTOR DE SALIDAS GRUPALES   #
#Este bloque de código funciona como un planificador de eventos. Su misión es recolectar el 
# nombre y la fecha de una nueva salida del club desde un formulario y enviarlos a la base de
# datos para que queden programados, confirmando la creación con un mensaje de éxito para que 
# todos sepan hacia dónde patinarán.
@app.route('/crear_ruta', methods=['POST'])
def crear_ruta():
    nombre = request.form.get('nombre_ruta')
    fecha = request.form.get('fecha_ruta')
    
    if logic.crear_nueva_ruta(nombre, fecha):
        flash(f"🗺️ Ruta '{nombre}' creada con éxito", "success")
    else:
        flash("❌ Error al crear la ruta", "danger")
    
    return redirect(url_for('rutas'))




#   CATALOGO DE RECORRIDOS PROGRAMADOS   #
#Este código funciona como el visualizador de la agenda. Se encarga de solicitar a la base 
# de datos todas las rutas o recorridos programados y los envía directamente a la pantalla 
# de "rutas" para que los usuarios puedan consultar los próximos destinos del club.
@app.route('/rutas')
def rutas():
    # Le pedimos a logic que nos traiga la lista
    lista_de_rutas = logic.obtener_rutas()
    # Se la pasamos al HTML
    return render_template('rutas.html', rutas=lista_de_rutas)




#   ELIINADOR DE RUTAS AGENDADAS   #
#Este bloque de código funciona como un limpiador de agenda. Su tarea es recibir el identificador 
# de una ruta específica, dar la orden de borrarla definitivamente de la base de datos y 
# refrescar la pantalla para que el usuario confirme que el recorrido ya no forma parte de 
# la programación.
@app.route('/eliminar_ruta/<id_ruta>', methods=['POST'])
def eliminar_ruta(id_ruta):
    if logic.borrar_ruta(id_ruta):
        flash("🗑️ Ruta eliminada", "info")
    else:
        flash("❌ No se pudo eliminar la ruta", "danger")
    
    return redirect(url_for('rutas'))






#   PREPARADOR DE LISTA DE ASISTENCIA   #
#Esta función actúa como el preparador del pase de lista. Su trabajo es reunir dos piezas de 
# información clave: los detalles de una ruta específica y la lista completa de alumnos ordenada 
# alfabéticamente; luego, envía todo esto a una pantalla especial para que puedas seleccionar 
# quiénes asistieron a ese recorrido.
@app.route('/marcar_ruta/<id_ruta>')
def marcar_ruta(id_ruta):
    # 1. Buscamos los datos de la ruta específica
    ruta = logic.db.rutas.find_one({"_id": logic.ObjectId(id_ruta)})
    # 2. Buscamos a todos los alumnos para mostrarlos en la lista
    todos_los_alumnos = list(logic.db.alumnos.find().sort("nombre", 1))
    
    return render_template('marcar_asistencia_ruta.html', 
                           ruta=ruta, 
                           alumnos=todos_los_alumnos,
                           id_ruta=id_ruta)







#   REGISTRO MASIVO DE ASISTENTES   #
#Este bloque de código funciona como el notario de la ruta. Se encarga de recibir la lista 
# de todos los alumnos que seleccionaste, busca la ruta específica en la base de datos y 
# guarda permanentemente esos nombres dentro de ella, confirmando con un mensaje que la 
# asistencia ha sido registrada con éxito.
@app.route('/guardar_asistencia_ruta/<id_ruta>', methods=['POST'])
def guardar_asistencia_ruta(id_ruta):
    # Recibimos la lista de IDs de alumnos seleccionados
    asistentes_ids = request.form.getlist('asistentes')
    
    # Actualizamos la ruta en la base de datos
    logic.db.rutas.update_one(
        {"_id": logic.ObjectId(id_ruta)},
        {"$set": {"asistentes": asistentes_ids}}
    )
    flash("✅ Asistencia de la ruta actualizada", "success")
    return redirect(url_for('rutas'))









@app.route('/actualizar_foto', methods=['POST'])
def actualizar_foto():
    id_alumno = request.form.get('id_alumno')
    archivo = request.files.get('nueva_foto')
    
    # Imprimimos para ver si el cambio en el HTML funcionó
    print(f"🕵️‍♂️ VALIDACIÓN FINAL: ID recibido = '{id_alumno}'")

    if archivo and id_alumno and id_alumno.strip() != "":
        try:
            res = cloudinary.uploader.upload(archivo, folder="rollers_powerfull")
            nueva_url = res.get('secure_url')
            
            # Mandamos el ID limpio a la lógica
            logic.actualizar_foto_db(id_alumno.strip(), nueva_url)
            flash("📸 ¡Foto actualizada!", "success")
        except Exception as e:
            print(f"❌ Error: {e}")
            flash("Error al subir", "danger")
    else:
        print("⚠️ SIGUE LLEGANDO VACÍO. Revisa el nombre de la variable en el loop del HTML.")
            
    return redirect(url_for('home'))







@app.route('/registrar_pago_manual', methods=['POST'])
def registrar_pago_manual():
    datos = request.json
    # Usamos logic.registrar_pago (sin el _completo)
    exito = logic.registrar_pago(
        datos.get('id_alumno'), 
        datos.get('monto'), 
        datos.get('tipo'), 
        datos.get('fecha')
    )
    return jsonify({"success": exito})





@app.route('/actualizar_nivel', methods=['POST'])
def actualizar_nivel():
    data = request.get_json()
    from bson import ObjectId
    
    db.alumnos.update_one(
        {"_id": ObjectId(data['id'])},
        {"$set": {"nivel_roller": data['nivel']}}
    )
    return jsonify({"success": True})





#   ACTIVACION DE SERVIDOR LOCAL   #
#Este bloque de código funciona como el interruptor principal del sistema. Su trabajo es detectar 
# si estás ejecutando el archivo directamente para encender el servidor web, activando el modo 
# de "depuración" para ver errores en tiempo real y abriendo una puerta en el puerto 5000 para 
# que puedas usar la aplicación en tu navegador.
if __name__ == '__main__':
    # host='0.0.0.0' es el código mágico para permitir acceso desde el celular en tu misma red Wi-Fi
    app.run(debug=True, host='0.0.0.0', port=5000)