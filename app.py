from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
# Si es necesario, pip install Werkzeug 
from werkzeug.utils import secure_filename 
# No es necesario instalar, es parte del sistema standard de Python 
import os 
import time

app = Flask(__name__)
CORS(app)

class Usuario:

  def __init__(self, host, user, password, database,port):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        

        self.cursor = self.conn.cursor()
        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
        (codigo INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(15) NOT NULL,
        apellido VARCHAR(15) NOT NULL,
        sexo VARCHAR(15) NOT NULL,
        fechaNacimiento DATE NOT NULL,
        pais VARCHAR(15) NOT NULL,
        imagen VARCHAR(50) NOT NULL,
        email VARCHAR(30) NOT NULL)''')
        self.conn.commit()

        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

  def agregar_Usuario(self,nombre,apellido,sexo,fechaNacimiento,pais,imagen,email):

    sql ="INSERT INTO usuarios (nombre,apellido,sexo,fechaNacimiento,pais,imagen,email) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    valores = (nombre,apellido,sexo,fechaNacimiento,pais,imagen,email)
    self.cursor.execute(sql,valores)
    self.conn.commit()
    return self.cursor.lastrowid

  def modificar_usuario(self, codigo, nvo_nombre, nvo_apellido, nvo_sexo, nvo_fechaNacimiento, nvo_pais,nva_imagen,nvo_email):

        sql = "UPDATE usuarios SET nombre = %s , apellido = %s , sexo = %s , fechaNacimiento = %s , pais = %s, imagen = %s , email = %s WHERE codigo = %s"
        valores = (nvo_nombre,nvo_apellido,nvo_sexo,nvo_fechaNacimiento,nvo_pais,nva_imagen,nvo_email,codigo)
        self.cursor.execute(sql,valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

  def eliminar_usuario(self, codigo):
      self.cursor.execute(f"DELETE FROM usuarios WHERE codigo = {codigo}");
      self.conn.commit()
      return self.cursor.rowcount > 0

  def obtener_Usuario(self, codigo):
    self.cursor.execute(f"SELECT * FROM usuarios WHERE codigo = {codigo}")
    return self.cursor.fetchone()


  def obtener_Usuarios(self):
    self.cursor.execute("SELECT * FROM usuarios")
    return self.cursor.fetchall()

user = Usuario(host='localhost', user='root', password='', database='ddbb_usuarios', port= 3307)

ruta_destino = './static/img/UsuarioImages/'


@app.route("/", methods=['GET'])
def home():
  return render_template("index.html")

@app.route("/calendario", methods=['GET'])
def calendario():
  return render_template("cronograma.html")

@app.route("/equiposypilotos", methods=['GET'])
def equiposypilotos():
  return render_template("equipos.html")

@app.route("/estadisticas", methods=['GET'])
def estadisticas():
  return render_template("estadisticas.html")

@app.route("/galeria", methods=['GET'])
def galeria():
  return render_template("galeria.html")

@app.route("/administrador", methods=['GET'])
def administrador():
  return render_template("administrador.html")

@app.route("/contacto", methods=['GET','POST'])
def agregar_Usuario():

  if request.method == 'POST':
    
    imagen= request.files['imagen'];
    nombre_imagen= ''
    
    nombre_imagen = secure_filename(imagen.filename)
    nombre_base, extension = os.path.splitext(nombre_imagen) 
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"

    fname = request.form['nombre'].lower()
    lname = request.form['apellido'].lower()
    sex = request.form['sexo'].lower()
    birthday = request.form['fecha_nacimiento'].lower()
    country = request.form['pais'].lower()
    email = request.form['email'].lower()
    
    user.agregar_Usuario(fname,lname,sex,birthday,country,nombre_imagen,email)
    
    imagen.save(os.path.join(ruta_destino, nombre_imagen))
    
  return render_template("contacto.html")

@app.route("/contacto/<int:codigo>", methods=["DELETE"])
def eliminar_usuario(codigo):

  if request.method == 'DELETE':
    user.eliminar_usuario(codigo);
  return render_template("administrador.html")


@app.route("/contacto/<int:codigo>", methods=["PUT"])
def modificar_usuario(codigo):

    nombre_imagen= '' 
    imagen= '' 
    if 'imagen' not in request.files:
      print('no hay archivo')
    # Verifica si se proporcionó una nueva imagen
    else: 
      imagen = request.files['imagen']
        
        # Procesamiento de la imagen
    nombre_imagen = secure_filename(imagen.filename) 
    nombre_base, extension = os.path.splitext(nombre_imagen) 
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" 
      
        # Guardar la imagen en el servidor
    imagen.save(os.path.join(ruta_destino, nombre_imagen)) 


    fname = request.form['nombre'].lower()
    lname = request.form['apellido'].lower()
    sex = request.form['sexo'].lower()
    birthday = request.form['fecha_nacimiento'].lower()
    country = request.form['pais'].lower()
    email = request.form['email'].lower()
    
  
    user.modificar_usuario(codigo,fname,lname,sex,birthday,country,nombre_imagen,email)
  
    return render_template("administrador.html")


@app.route("/usuarios", methods=['GET'])
def listar_usuarios():
  users = user.obtener_Usuarios();
  return jsonify(users)


@app.route("/usuarios/<int:codigo>", methods=['GET'])
def obtener_usuario(codigo):
  usuario = user.obtener_Usuario(codigo)
  return jsonify(usuario)


if __name__ == "__main__":
  app.run(debug=True)