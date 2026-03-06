"""
PROYECTO: PowerFull Club - Sistema de Gestión de Rollers
ARCHIVO: logic.py
DESCRIPCIÓN: Capa de persistencia (Base de Datos). 
             Contiene las funciones CRUD (Crear, Leer, Eliminar) 
             conectadas a MongoDB Atlas.
""

"""


#    LIBRERIAS DE CONEXION BASE   #
# Este bloque de código es el encabezado de importaciones de tu archivo de lógica. No ejecuta acciones
# visuales, sino que trae al proyecto las herramientas necesarias para que Python pueda "hablar" con la
# base de datos y manejar el tiempo.
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv








#     Conexión segura a MongoDB.     #
#"Este bloque inicializa la seguridad del sistema cargando las credenciales ocultas desde el 
# archivo .env. Posteriormente, utiliza esa llave protegida (MONGO_URI) para establecer una 
# conexión autenticada con MongoDB Atlas, asignando la base de datos principal y capturando 
# cualquier fallo de red para evitar que la aplicación colapse repentinamente."
# 1. ABRIMOS LA BÓVEDA
load_dotenv()

# 2. Sacamos la llave de MongoDB del .env
MONGO_URI = os.getenv("MONGO_URI")

# 3. Intento de conexión segura
try:
    client = MongoClient(MONGO_URI)
    db = client['PowerFullClub']
    coleccion = db['alumnos']
    print("✅ Conexión exitosa: El túnel a MotoTech-DB está abierto y BLINDADO. 🛡️")
except Exception as e:
    print(f"❌ Error de conexión a la nube: {e}")



    




#  REGISTRO DE DATOS PROTEGIDOS   #
# Es la función encargada de escribir y asegurar la información dentro de la base de datos de
# forma permanente. Recibe el paquete de datos del alumno y lo inserta como un nuevo registro
# en la colección, confirmando mediante un mensaje que la operación fue exitosa.
def guardar_alumno(datos):
    try:
        # 🕵️‍♂️ PUNTO DE CONTROL: Revisamos el sobre antes de guardarlo
        print(f"📦 Recibiendo expediente de: {datos.get('nombre', 'Desconocido')}")
        print(f"📸 URL de la foto recibida: '{datos.get('foto', 'NINGUNA')}'")

        # Seguro anti-fallos: Si por alguna razón app.py olvidó mandar el campo "foto", lo creamos vacío
        if "foto" not in datos:
            datos["foto"] = ""

        # Intentamos meter el sobre en el archivador
        coleccion.insert_one(datos)
        print(f"✅ Expediente completo guardado exitosamente en Atlas.")

    except Exception as e:
        # Si algo falla (ej. se cae el Wi-Fi), atrapamos el error aquí
        print(f"❌ Error al intentar guardar en la nube: {e}")




#   SEMAFORO DE PAGOS AUTOMATICOS   #
# Ejecuta una consulta de recuperación masiva en MongoDB para extraer la lista completa de
# registros almacenados. Transforma los datos crudos de la base de datos en un formato de lista
# compatible con Python y garantiza la estabilidad del sitio devolviendo una lista vacía en caso
# de error, evitando que la aplicación se bloquee por fallos de red.
def obtener_alumnos_con_estado_pago():
    """Trae a los alumnos incluyendo su estado de pago actual (Semáforo optimizado para móviles)."""
    try:
        # 1. Traemos la lista básica de alumnos (VIAJE 1 A LA NUBE)
        alumnos = list(coleccion.find().sort("nombre", 1))
        print(f"DEBUG: MongoDB encontró {len(alumnos)} alumnos")

        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        
        # 2. Traemos TODOS los pagos vigentes de una vez (VIAJE 2 A LA NUBE)
        # Usamos $gte para traer solo pagos no vencidos, ordenados del más reciente al más antiguo
        pagos_vigentes = list(db.pagos.find(
            {"fecha_vencimiento": {"$gte": fecha_hoy}}
        ).sort("fecha_vencimiento", -1))

        # 3. 🧠 EL DICCIONARIO EN RAM (El secreto de la velocidad)
        # Organizamos los recibos en carpetas con el ID del alumno
        mapa_pagos = {}
        for pago in pagos_vigentes:
            id_alu = str(pago.get("alumno_id") or pago.get("id_alumno"))
            if id_alu not in mapa_pagos:
                mapa_pagos[id_alu] = pago # Guardamos solo el pago más reciente

        lista_con_pagos = []

        for alu in alumnos:
            # Extraemos el ID como texto
            id_str = str(alu["_id"])

            # En lugar de ir a la base de datos, buscamos en nuestra RAM (¡Es instantáneo!)
            ultimo_pago = mapa_pagos.get(id_str)

            # 4. Decidimos el color del semáforo
            if ultimo_pago:
                # Leemos el tipo de pago y lo pasamos a minúsculas para analizarlo
                tipo_pago = str(ultimo_pago.get("tipo", "")).lower()

                if "mensual" in tipo_pago:
                    estado = "Plan Mensual Activo"
                    color = "success"  # Verde brillante
                elif "semanal" in tipo_pago:
                    estado = "Plan Semanal Activo"
                    color = "primary"  # Azul oscuro
                else:
                    estado = "Clase Ocasional"
                    color = "info"    # Azul claro/Cian
            else:
                estado = "Pago Pendiente"
                color = "danger"      # Rojo alerta

            # 🔥 EL CAMBIO MÁGICO 🔥 (Tu lógica original intacta)
            # En lugar de crear un objeto nuevo incompleto, usamos el mismo que trajo la base de datos
            # Solo le convertimos el _id a texto y le pegamos el estado del pago.
            alu["_id"] = id_str 
            alu["estado_pago"] = estado
            alu["color_pago"] = color

            # Ahora metemos a la lista a 'alu' COMPLETO (ya lleva su cedula, su foto, etc.)
            lista_con_pagos.append(alu)

        return lista_con_pagos

    except Exception as e:
        print(f"❌ Error al obtener alumnos con pagos: {e}")
        return []



    

#    LIMPIEZA Y CONTROL DIARIO    #
# Realiza una operación de supresión dirigida convirtiendo el identificador de texto en un objeto
# compatible con la base de datos. Utiliza una estructura de seguridad para interceptar posibles
# fallos en el formato del ID o en la conexión, asegurando que la acción de borrado sea precisa,
# irreversible y segura.
def borrar_alumno(id_recibido):
    try:
        # Convertimos el texto del ID en un formato que MongoDB entienda
        id_formateado = ObjectId(id_recibido)

        # Le damos la orden a la colección de eliminar
        coleccion.delete_one({"_id": id_formateado})

        # Mensaje de confirmación en la consola
        print(f"✅ Alumno con ID {id_recibido} eliminado con éxito.")

    except Exception as e:
        # Si el ID está mal escrito o falla la red, atrapamos el error
        print(f"❌ Error al intentar eliminar: {e}")







def guardar_asistencia(id_alumno, fecha):
    try:
        # Usamos 'db' que es la que se conectó con tu clave real arriba
        db.asistencias.insert_one({
            "id_alumno": ObjectId(id_alumno),
            "fecha": fecha,
            "asistio": True
        })
    except Exception as e:
        print(f"Error: {e}")






def obtener_historial_asistencias():
    try:
        asistencias = list(db.asistencias.find().sort(
            "fecha", -1))  # Trae las más recientes primero
        historial_completo = []

        for asis in asistencias:
            # Buscamos el nombre del alumno usando el id_alumno que guardamos
            alumno = coleccion.find_one({"_id": ObjectId(asis['id_alumno'])})

            historial_completo.append({
                "nombre": alumno['nombre'] if alumno else "Alumno Eliminado",
                "fecha": asis['fecha'],
                "id": asis['_id']
            })
        return historial_completo
    except Exception as e:
        print(f"❌ Error al obtener historial: {e}")
        return []





#   CONVERSOR DE DATOS GRAFICO  PARA EL CALENDARIO DE HISTORIAL   #
# Este bloque funciona como el traductor de registros a eventos. Su tarea es escanear tu base de datos de
# asistencias, extraer el nombre del alumno y la fecha, y "empaquetarlos" con colores y formatos específicos
# para que el calendario sepa exactamente qué etiqueta poner y en qué día debe pegarla.
def listar_eventos_calendario():
    try:
        from datetime import datetime 
        
        # 1. Traemos todo de la base de datos
        asistencias = list(db.asistencias.find())
        alumnos = list(db.alumnos.find())
        todos_los_pagos = list(db.pagos.find())
        
        # 2. MAPA DE ALUMNOS (Para no perder el nombre)
        mapa_nombres = {}
        for alu in alumnos:
            mapa_nombres[str(alu["_id"])] = alu.get("nombre", "Alumno Desconocido")

        # 3. MAPA DE PAGOS EXTREMO (Soporta errores de nombre de ID)
        pagos_por_alumno = {}
        for pago in todos_los_pagos:
            # Buscamos el ID del alumno sin importar cómo lo haya guardado la BD
            id_alu_pago = str(pago.get("id_alumno") or pago.get("alumno_id") or "").strip()
            if id_alu_pago not in pagos_por_alumno:
                pagos_por_alumno[id_alu_pago] = []
            pagos_por_alumno[id_alu_pago].append(pago)

        print(f"DEBUG: Procesando {len(asistencias)} asistencias para el calendario Premium")

        agrupados_por_fecha = {}

        # 4. RECORREMOS ASISTENCIAS Y CRUZAMOS CON PAGOS
        for asis in asistencias:
            # Validamos que sí haya asistido
            if str(asis.get("asistio")).lower() not in ["true", "1", "yes"] and asis.get("asistio") != True:
                continue
                
            asis_id = str(asis["_id"])
            
            # Extraemos ID y Fecha de la asistencia blindados contra errores
            id_alu = str(asis.get("id_alumno") or asis.get("alumno_id") or "").strip()
            nombre_real = mapa_nombres.get(id_alu, "Alumno Desconocido")
            fecha_raw = str(asis.get("fecha", ""))[:10].strip() # Ej: "2026-03-01"
            
            if not fecha_raw:
                continue

            # 🟢🔴 MÁQUINA DEL TIEMPO FINANCIERA (VERSIÓN TANQUE)
            estado_pago = "Debe"
            color_pago = "danger" 
            
            pagos_del_alumno = pagos_por_alumno.get(id_alu, [])
            
            for pago in pagos_del_alumno:
                # Extraemos las fechas limpiando horas y espacios
                f_pago = str(pago.get("fecha_pago") or pago.get("fecha") or "").strip()[:10]
                f_vence = str(pago.get("fecha_vencimiento") or f_pago).strip()[:10]
                tipo_pago = str(pago.get("tipo", "")).lower()
                
                coincide = False
                
                # REGLA 1: Si es un pago MENSUAL, miramos solo el Año y el Mes (Ej: "2026-03" == "2026-03")
                if "mensual" in tipo_pago and f_pago[:7] == fecha_raw[:7]:
                    coincide = True
                # REGLA 2: Si es Diario o Semana, verificamos si coinciden exactamente ese día o está en el rango
                elif f_pago == fecha_raw:
                    coincide = True
                elif f_pago and f_vence and (f_pago <= fecha_raw <= f_vence):
                    coincide = True

                # Si alguna regla funcionó, aplicamos los colores y salimos del ciclo de pagos
                if coincide:
                    if "mensual" in tipo_pago:
                        estado_pago = "Mes Pagado"
                        color_pago = "success" # Verde
                    elif "semana" in tipo_pago:
                        estado_pago = "Semana Pagada"
                        color_pago = "primary" # Azul oscuro
                    else:
                        estado_pago = "Día Pagado"
                        color_pago = "info" # Cian
                    break 

            # Evitamos duplicados en la lista visual del mismo día
            if fecha_raw not in agrupados_por_fecha:
                agrupados_por_fecha[fecha_raw] = []
            
            ya_existe = any(item.get("nombre") == nombre_real for item in agrupados_por_fecha[fecha_raw])
            
            if not ya_existe:
                agrupados_por_fecha[fecha_raw].append({
                    "id_asistencia": asis_id,
                    "nombre": nombre_real,
                    "estado": estado_pago,
                    "color": color_pago
                })

        # 5. ENVIAMOS AL CALENDARIO
        eventos = []
        for fecha, lista_detalle in agrupados_por_fecha.items():
            eventos.append({
                'title': f"👥 {len(lista_detalle)} Patinadores",
                'start': fecha,
                'backgroundColor': '#00f2ff', 
                'borderColor': '#008b99',
                'textColor': '#000000',
                'extendedProps': {
                    'cantidad': len(lista_detalle),
                    'lista_asistencias': lista_detalle 
                }
            })

        return eventos
    except Exception as e:
        print(f"ERROR CRÍTICO en calendario: {e}")
        return []
    




#   CORRECCION DE ASISTENCIA ERRONEA   #
#Esta función actúa como el "botón de corrección" para el profesor. Si por error marcó a un alumno que no 
# fue a clase, este código busca el registro exacto en la base de datos de la nube y lo elimina 
# permanentemente, asegurando que las estadísticas y el historial sean reales y precisos.
def borrar_asistencia(id_recibido):
    try:
        # Convertimos el ID de texto a objeto de MongoDB
        id_formateado = ObjectId(id_recibido)
        # Borramos específicamente de la colección de asistencias
        db.asistencias.delete_one({"_id": id_formateado})
        print(f"✅ Asistencia {id_recibido} eliminada de la nube.")
    except Exception as e:
        print(f"❌ Error al eliminar asistencia: {e}")









#   CALCULO DE VIGENCIA  FINANCIERA   #
#Esta función actúa como el Cajero Inteligente del club. Su trabajo principal es recibir un pago y 
# calcular automáticamente hasta qué día tiene permiso el alumno para patinar: si es mensualidad le 
# otorga 30 días, y si es una clase suelta, el permiso vence al terminar el día actual.
def registrar_pago(id_alumno, monto, tipo, fecha_personalizada=None):
    try:
        from datetime import datetime
        from bson.objectid import ObjectId
        
        # PASO 0: Buscar al alumno
        filtro = {"_id": ObjectId(id_alumno)}
        alumno = db.alumnos.find_one(filtro)
        
        if not alumno:
            alumno = db.alumnos.find_one({"id": id_alumno})
            filtro = {"id": id_alumno}

        nombre_alumno = alumno.get('nombre', 'Desconocido') if alumno else "Alumno no encontrado"

        # LA FECHA
        fecha_final = fecha_personalizada if fecha_personalizada else datetime.now().strftime("%Y-%m-%d")
        hora_actual = datetime.now().strftime("%H:%M:%S")

        # 1. Guardar el Pago
        db.pagos.insert_one({
            "alumno_id": str(id_alumno),
            "nombre": nombre_alumno,
            "monto": int(monto),
            "tipo": tipo,
            "fecha": fecha_final,
            "hora": hora_actual
        })

        # 2. Actualizar estado (Semáforo verde)
        db.alumnos.update_one(
            filtro,
            {"$set": {"estado_pago": "Al día", "color_pago": "success"}}
        )
        
        # 🚀 3. EL CALENDARIO (CON EL MOLDE EXACTO)
        # Revisamos si ya vino ese día
        asistencia_existente = db.asistencias.find_one({
            "id_alumno": ObjectId(id_alumno), 
            "fecha": fecha_final
        })
        
        # Si no tiene asistencia ese día, la creamos como le gusta al calendario
        if not asistencia_existente:
            db.asistencias.insert_one({
                "id_alumno": ObjectId(id_alumno), # <-- El formato estricto
                "fecha": fecha_final,             # <-- La fecha que elegiste
                "asistio": True                   # <-- La llave mágica
            })
            print(f"🗓️ Asistencia inyectada en el calendario para el {fecha_final}")
        
        print(f"✅ Pago y asistencia guardados ({fecha_final}) para: {nombre_alumno}")
        return True

    except Exception as e:
        print(f"❌ Error en logic.registrar_pago: {e}")
        return False
    







#    HISTORIAL RECIENTE  DE COBROS   #
#Esta función funciona como el Libro Contable de la aplicación. Se encarga de revisar los registros más 
# recientes en la nube y, mediante un cruce de datos, vincula cada transacción de dinero con el nombre 
# del alumno correspondiente para que el profesor sepa exactamente quién pagó.

# Pégalo al final de logic.py
def obtener_historial_pagos():
    # Buscamos en la colección 'pagos'
    # Ordenamos por fecha descendente (-1) y luego por hora
    # Limitamos a 10 para que no sea infinito
    try:
        historial = list(db.pagos.find().sort([("fecha", -1), ("hora", -1)]).limit(10))
        return historial
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        return []








#   ANULACION DEFINITIVA DE COBRO   #
# Esta función es el ejecutor de limpieza. Su único trabajo es tomar el identificador (ID) que
# le envía la aplicación, buscar ese registro exacto en la colección de "pagos" y borrarlo de
# la base de datos. Si algo sale mal (como un error de conexión), captura el fallo y avisa para
# evitar que el programa se detenga.
def borrar_pago(id_pago):
    try:
        # Borramos el documento que coincida con el ID
        db.pagos.delete_one({"_id": ObjectId(id_pago)})
        return True
    except Exception as e:
        print(f"Error al borrar pago: {e}")
        return False









#    PLANIFICACION DE EVENTOS GRUPALES   #
#Esta función es el Organizador de Eventos de tu aplicación. Permite al profesor planificar salidas 
# grupales o recorridos especiales, creando un espacio específico en la base de datos donde se irán 
# sumando los patinadores que participen en cada jornada.
def crear_nueva_ruta(nombre, fecha):
    try:
        nueva_ruta = {
            "nombre": nombre,
            "fecha": fecha,
            "asistentes": []  # Empezamos con la lista de alumnos vacía
        }
        # Usamos una nueva colección llamada 'rutas'
        db.rutas.insert_one(nueva_ruta)
        return True
    except Exception as e:
        print(f"❌ Error al crear ruta en logic: {e}")
        return False
    





    
#   LISTADO DE RUTAS PROGRAMADAS  #
#Esta función es el Catálogo de Salidas de tu aplicación. Se encarga de extraer todas las rutas guardadas 
# en la nube y prepararlas para que el profesor las vea en su celular, asegurándose de que las más 
# recientes aparezcan siempre al principio.
def obtener_rutas():
    try:
        # Buscamos todas las rutas y las convertimos en una lista
        rutas_db = list(db.rutas.find().sort("fecha", -1))

        # Convertimos los IDs a texto aquí mismo para que app.py no trabaje de más
        for r in rutas_db:
            r["id"] = str(r["_id"])

        return rutas_db
    except Exception as e:
        print(f"❌ Error al obtener rutas: {e}")
        return []



#   ELIMINACION DE EVENTOS PROGRAMADOS   #
#Esta función es el Cancelador de Eventos. Su única misión es localizar una ruta específica mediante su 
# identificador único y eliminarla por completo de la base de datos, ideal para cuando un evento se 
# suspende o se registró por error.
def borrar_ruta(id_ruta):
    try:
        db.rutas.delete_one({"_id": ObjectId(id_ruta)})
        return True
    except Exception as e:
        print(f"❌ Error al borrar ruta: {e}")
        return False










#   Generador de estadísticas grupales.   #
#Este bloque funciona como el motor analítico de la aplicación. Extrae y cruza los datos 
# de todos los alumnos y sus asistencias para generar métricas en tiempo real. Calcula el 
# volumen total mensual, identifica el 'Top 3' de patinadores con mejor rendimiento y genera 
# alertas automáticas para los alumnos que no han asistido en los últimos 7 días.
def obtener_estadisticas_profe():
    try:
        asistencias = list(db.asistencias.find())
        alumnos = list(db.alumnos.find())
        ahora = datetime.now()
        hace_siete_dias = ahora - timedelta(days=7)

        # 1. TRADUCTOR MÁGICO: Vincula IDs con Nombres
        mapa_nombres = {}
        for alu in alumnos:
            id_str = str(alu.get('_id'))
            id_normal = str(alu.get('id', ''))
            nombre = alu.get('nombre', 'Desconocido')
            mapa_nombres[id_str] = nombre
            if id_normal:
                mapa_nombres[id_normal] = nombre

        total_mes = 0 
        conteo_nombres_mes = {}
        ultimas_fechas_id = {} # AHORA BUSCAMOS POR ID

        for asis in asistencias:
            # Extraemos el ID de la asistencia
            id_alu = str(asis.get('alumno_id') or asis.get('id_alumno') or "")
            
            # Buscamos el nombre real usando el traductor mágico
            nombre = mapa_nombres.get(id_alu, "Alumno Desconocido")
            
            fecha_raw = asis.get('fecha_entrenamiento') or asis.get('fecha')
            fecha_str = str(fecha_raw)

            # Limpieza de fecha
            if '/' in fecha_str:
                p = fecha_str.split('/')
                f_limpia = f"{p[2]}-{p[1]}-{p[0]}" if len(p) == 3 else fecha_str[:10]
            else:
                f_limpia = fecha_str[:10]

            try:
                f_dt = datetime.strptime(f_limpia, '%Y-%m-%d')

                # GUARDAMOS LA FECHA USANDO EL ID
                if id_alu:
                    if id_alu not in ultimas_fechas_id or f_dt > ultimas_fechas_id[id_alu]:
                        ultimas_fechas_id[id_alu] = f_dt

                # SUMAMOS AL TOP RENDIMIENTO Y VOLUMEN DEL MES
                if f_dt.month == ahora.month and f_dt.year == ahora.year:
                    total_mes += 1
                    conteo_nombres_mes[nombre] = conteo_nombres_mes.get(nombre, 0) + 1

            except Exception as e:
                continue 

        # Ordenamos el Top 3
        top_alumnos = sorted(conteo_nombres_mes.items(), key=lambda x: x[1], reverse=True)[:3]

        # 2. EVALUAR AUSENCIAS USANDO EL ID
        alertas = []
        for alu in alumnos:
            nombre_alu = alu.get('nombre', 'Desconocido')
            id_str = str(alu.get('_id'))
            id_normal = str(alu.get('id', ''))
            
            # Verificamos si alguno de sus IDs tiene una fecha guardada
            fecha_ultima = ultimas_fechas_id.get(id_str) or ultimas_fechas_id.get(id_normal)

            if fecha_ultima:
                # Si vino hace más de 7 días, alerta roja
                if fecha_ultima < hace_siete_dias:
                    alertas.append(nombre_alu)
            else:
                # Si no hay registro de fecha, nunca ha venido
                alertas.append(nombre_alu)

        return {
            "total_mes": total_mes,
            "top_alumnos": top_alumnos,
            "alertas": alertas[:5]
        }
    except Exception as e:
        print(f"❌ ERROR EN STATS: {e}")
        return {"total_mes": 0, "top_alumnos": [], "alertas": []}









#    CONSULTA DE PAGOS RECIENTES    #
#"Esta función extrae de la base de datos un registro rápido de los últimos 10 pagos realizados. 
# Utiliza un doble filtro de ordenamiento cronológico (por fecha y hora de forma descendente) para 
# garantizar que los cobros más recientes aparezcan siempre de primeros, limitando la búsqueda para 
# no saturar la memoria del servidor."
def obtener_historial_pagos():
    # Buscamos en la colección 'pagos'
    # Ordenamos por fecha descendente (-1) y luego por hora
    # Limitamos a 10 para que no sea infinito
    try:
        historial = list(db.pagos.find().sort([("fecha", -1), ("hora", -1)]).limit(10))
        return historial
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        return []
    



 #   HISTORIAL OPTIMIZADO DE PAGOS      #
#"Este bloque optimiza la extracción del historial financiero. Descarga los últimos 30 pagos y utiliza 
# un diccionario en memoria RAM para cruzar los identificadores (IDs) con los nombres reales de los 
# alumnos al instante. Además, formatea y estandariza los datos (fechas, montos y tipos) para que la 
# interfaz web los procese sin esfuerzo ni demoras."
def obtener_ultimos_pagos():
    """Trae el historial de pagos cruzando el ID con el nombre real del alumno."""
    try:
        # 1. Traemos los últimos 30 pagos de MongoDB, ordenados del más nuevo al más viejo
        pagos = list(db.pagos.find().sort("fecha_pago", -1).limit(30))
        
        # 2. Traemos a los alumnos para saber sus nombres (Diccionario en RAM = 0 demoras)
        alumnos = list(db.alumnos.find())
        mapa_nombres = {str(alu["_id"]): alu.get("nombre", "Desconocido") for alu in alumnos}
        
        pagos_formateados = []
        for pago in pagos:
            pago["_id"] = str(pago["_id"])
            
            # Buscamos de quién es este pago
            id_alu = str(pago.get("alumno_id") or pago.get("id_alumno") or "")
            
            # INYECCIÓN 1: Le pegamos el nombre real para que el HTML lo pueda leer
            pago["nombre_alumno"] = mapa_nombres.get(id_alu, "Alumno Eliminado")
            
            # INYECCIÓN 2: Aseguramos que las fechas tengan el nombre exacto que pide el HTML
            pago["fecha_pago"] = pago.get("fecha_pago") or pago.get("fecha", "---")
            pago["fecha_vencimiento"] = pago.get("fecha_vencimiento") or pago.get("vencimiento", "---")
            
            # Aseguramos el tipo y monto por si acaso
            pago["tipo"] = pago.get("tipo", "General")
            pago["monto"] = pago.get("monto", 0)

            pagos_formateados.append(pago)
            
        return pagos_formateados
    except Exception as e:
        print(f"❌ Error al obtener pagos: {e}")
        return []
    






#   ACTUALIZACION DE FOTO DEL PERFIL   #   
#"Este bloque se encarga de enlazar la nueva imagen de perfil del alumno directamente en la base de datos. 
# Localiza el registro exacto utilizando su identificador único e irremplazable de MongoDB (ObjectId) y 
# actualiza únicamente la URL de la foto mediante una inyección segura ($set), garantizando que el resto 
# de los datos personales del patinador permanezcan intactos."
def actualizar_foto_db(id_alumno_str, nueva_url):
    """Actualiza la URL de la foto del alumno usando su ID único de MongoDB."""
    try:
        # Ahora buscamos directamente por el _id de MongoDB, no por la cédula
        db.alumnos.update_one(
            {"_id": ObjectId(id_alumno_str)}, 
            {"$set": {"foto": nueva_url}}
        )
        print(f"✅ Foto enlazada en la BD para el ID: {id_alumno_str}")
    except Exception as e:
        print(f"❌ Error al actualizar foto en BD: {e}")







def eliminar_asistencia(id_asistencia):
    """Busca una asistencia por su ID y la destruye en la base de datos."""
    try:
        from bson.objectid import ObjectId
        # Buscamos el documento exacto y lo borramos
        resultado = db.asistencias.delete_one({"_id": ObjectId(id_asistencia)})
        # Devuelve True si borró algo, False si no lo encontró
        return resultado.deleted_count > 0
    except Exception as e:
        print(f"❌ Error al eliminar asistencia: {e}")
        return False
    






def eliminar_alumno_total(id_alumno):
    """Borra a un alumno de la base de datos definitivamente."""
    try:
        from bson.objectid import ObjectId
        # 1. Borramos al alumno de la colección alumnos
        resultado = db.alumnos.delete_one({"_id": ObjectId(id_alumno)})
        
        # 2. (Opcional) Borrar sus asistencias para no dejar basura en la base de datos
        db.asistencias.delete_many({"id_alumno": id_alumno})
        
        return resultado.deleted_count > 0
    except Exception as e:
        print(f"❌ Error al eliminar alumno: {e}")
        return False
    




    # ==========================================================
# ASISTENCIA A RUTAS URBANAS
# ==========================================================

def obtener_ruta_por_id(id_ruta):
    """Busca una ruta específica para poder ver sus detalles."""
    try:
        ruta = db.rutas.find_one({"_id": ObjectId(id_ruta)})
        if ruta:
            ruta["id"] = str(ruta["_id"])
        return ruta
    except Exception as e:
        print(f"❌ Error al buscar ruta: {e}")
        return None





def obtener_nombres_alumnos():
    """Trae solo los nombres y IDs de los alumnos para la lista de asistencia."""
    try:
        # Traemos todos los alumnos ordenados alfabéticamente
        alumnos = list(db.alumnos.find().sort("nombre", 1))
        for alu in alumnos:
            alu["id"] = str(alu["_id"])
        return alumnos
    except Exception as e:
        print(f"❌ Error al obtener lista de alumnos: {e}")
        return []
    



    

def actualizar_asistentes_ruta(id_ruta, lista_asistentes):
    """Guarda la lista de alumnos que fueron a la ruta."""
    try:
        db.rutas.update_one(
            {"_id": ObjectId(id_ruta)},
            {"$set": {"asistentes": lista_asistentes}}
        )
        return True
    except Exception as e:
        print(f"❌ Error al guardar asistentes en la ruta: {e}")
        return False
    








def cambiar_estado_asistencia(id_asistencia, nuevo_estado):
    """
    Busca una asistencia por su ID y le actualiza el campo 'estado'.
    Si el campo no existía (porque son asistencias viejas), MongoDB lo crea automáticamente.
    """
    try:
        from bson.objectid import ObjectId
        db.asistencias.update_one(
            {"_id": ObjectId(id_asistencia)},
            {"$set": {"estado": nuevo_estado}}
        )
        print(f"✅ Estado de asistencia {id_asistencia} cambiado a {nuevo_estado}")
        return True
    except Exception as e:
        print(f"❌ Error al cambiar estado de asistencia: {e}")
        return False