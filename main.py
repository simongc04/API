import psycopg2
from flask import Flask, jsonify, request

# Login
# Crear proyecto
# Asignar gestor a proyecto
# Asignar cliente a proyecto
# Crear tareas a proyecto (debo estar asignado)
# Asignar programador a proyecto
# Asignar programadores a tareas
# Obtener programadores
# Obtener proyectos (activos o todos)
# Obtener tareas de un proyecto (sin asignar o asignada)

# Simón González Cabrera

app = Flask(__name__)

def ejecutar_sql(sql_text):
    host = "localhost"
    port = "5432"
    dbname = "alexsoft"
    user = "postgres"
    password = "postgres"

    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            options="-c search_path=public"
        )
        cursor = connection.cursor()

        cursor.execute(sql_text)

        if "UPDATE" in sql_text:
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'msg': 'Actualizado'})


        if "INSERT" in sql_text:
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'msg': 'Insertado '})

        columnas = [desc[0] for desc in cursor.description]

        resultados = cursor.fetchall()
        empleados = [dict(zip(columnas, fila)) for fila in resultados]

        cursor.close()
        connection.close()

        return jsonify(empleados)

    except psycopg2.Error as e:
        print("error", e)

        @app.route('/login', methods=['POST'])
        def gestor_login():
            body_request = request.json
            user = body_request["usuario"]
            passwd = body_request["passwd"]

            is_logged = ejecutar_sql(
                f"SELECT * FROM public.\"Gestor\" WHERE usuario = '{user}' AND passwd = '{passwd}';"
            )

            if len(is_logged.json) == 0:
                return jsonify({"msg": "No mi rey así no"})
            empleado = ejecutar_sql(
                f"SELECT * FROM public.\"Empleado\" WHERE id = '{is_logged.json[0]["empleado"]}';"
            )

            return jsonify(
                {
                    "id_empleado": empleado.json[0]["id"],
                    "id_gestor": is_logged.json[0]["id"],
                    "nombre": empleado.json[0]["nombre"],
                    "email": empleado.json[0]["email"]
                }
            )

@app.route('/crear_proyecto', methods=['POST'])
def crear_proyecto():
    body_request = request.json
    nombre = body_request["nombre"]
    descripcion = body_request["descripcion"]
    fecha_inicio = body_request["fecha_inicio"]
    cliente = body_request["cliente"]
    sql = f"""
        INSERT INTO public."Proyecto" (nombre, descripcion, fecha_creacion, fecha_inicio, fecha_finalizacion, cliente)
        VALUES (
            '{nombre}',
            '{descripcion}',
            NOW(),
            '{fecha_inicio}',
            null,
            {cliente},
        );
    """
    return (sql)

@app.route('/proyecto/programadores', methods=['GET'])
def obtener_programadores():

    return ejecutar_sql(
        f'SELECT * FROM public."Programador";'
    )


@app.route('/asignar_gestor', methods=['POST'])
def asignar_gestor_a_proyecto():
    try:
        datos = request.json
        gestor_id = datos.get('gestor')
        proyecto_id = datos.get('proyecto')

        consulta_gestor = f'SELECT id FROM public."Gestor" WHERE id = {gestor_id};'
        gestor_existente = ejecutar_sql(consulta_gestor)
        if not gestor_existente:
            return jsonify({"error": "El gestor especificado no existe"}), 404

        consulta_proyecto = f'SELECT id FROM public."Proyecto" WHERE id = {proyecto_id};'
        proyecto_existente = ejecutar_sql(consulta_proyecto)
        if not proyecto_existente:
            return jsonify({"error": "El proyecto especificado no existe"}), 404

        consulta_asignacion = f'''
        INSERT INTO public."GestoresProyecto" (gestor, proyecto, fecha_asignacion)
        VALUES ({gestor_id}, {proyecto_id}, CURRENT_TIMESTAMP);
        '''
        ejecutar_sql(consulta_asignacion)

        return jsonify({"mensaje": f"El gestor {gestor_id} ha sido asignado al proyecto {proyecto_id}"}), 201

    except psycopg2.Error as error:
        return jsonify({"error": f"Error al procesar la solicitud: {str(error)}"}), 500


@app.route('/proyecto/asignar_gestor_a_proyecto', methods=['POST'])
def asignar_gestor_a_proyecto():

    body_request = request.json
    Gestor = body_request["gestor"]
    Proyecto = body_request["proyecto"]
    sql = f"""
            INSERT INTO public."GestoresProyecto" (gestor, proyecto, fecha_asignacion)
            VALUES (
            
                {Gestor},
                {Proyecto},
                NOW()
            )
            
        """
    return jsonify(ejecutar_sql(sql))


@app.route('/proyecto/asignar_cliente_a_proyecto', methods=['POST'])
def asignar_cliente_a_proyecto():

    body_request = request.json
    ID_cliente = body_request["id_cliente"]
    ID_proyecto = body_request["id_proyecto"]
    sql = f"""
    
            UPDATE public."Proyecto"
            SET cliente = {ID_cliente}
            WHERE id = {ID_proyecto}
    
        """
    return jsonify(ejecutar_sql(sql))



# Asignar programadores a tareas


@app.route('/proyecto/asignar_programador_tarea', methods=['POST'])
def asignar_programador_tarea():
    body_request = request.json
    tarea = body_request["tarea"]
    programador = body_request["programador"]
    sql = f"""
            UPDATE public."Tarea"
            SET programador = {programador}
            WHERE id = {tarea}
        """
    return jsonify(ejecutar_sql(sql))


@app.route('/proyecto/programador_proyecto', methods=['POST'])
def asignar_programador_proyecto():
    body_request = request.json
    Programador = body_request["programador"]
    Proyecto = body_request["proyecto"]
    Fecha_Asignacion = body_request["fecha_asignacion"]

    sql = f"""
            INSERT INTO public."ProgramadoresProyecto" (programador, proyecto, fecha_asignacion)
			VALUES (
			
			{Programador}, 
			{Proyecto}, 
			'{Fecha_Asignacion}'
			
			)
			
        """
    return jsonify(ejecutar_sql(sql))





if __name__=='__main__':
    app.run(debug=True)