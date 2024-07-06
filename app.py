from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector


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
        email VARCHAR(30) NOT NULL)''')
        self.conn.commit()

        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

  def agregar_Usuario(self,nombre,apellido,sexo,fechaNacimiento,pais,email):

    sql ="INSERT INTO usuarios (nombre,apellido,sexo,fechaNacimiento,pais,email) VALUES (%s,%s,%s,%s,%s,%s)"
    valores = (nombre,apellido,sexo,fechaNacimiento,pais,email)
    self.cursor.execute(sql,valores)
    self.conn.commit()
    return self.cursor.lastrowid

  def modificar_usuario(self, codigo, nvo_nombre, nvo_apellido, nvo_sexo, nvo_fechaNacimiento, nvo_pais, nvo_email):

        sql = "UPDATE usuarios SET nombre = %s , apellido = %s , sexo = %s , fechaNacimiento = %s , pais = %s , email = %s WHERE codigo = %s"
        valores = (nvo_nombre,nvo_apellido,nvo_sexo,nvo_fechaNacimiento,nvo_pais,nvo_email, codigo)
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

    user.agregar_Usuario(request.form['nombre'].lower(),request.form['apellido'].lower(),request.form['sexo'].lower(),request.form['fecha_nacimiento'],request.form['pais'].lower(),request.form['email'].lower())
  return render_template("contacto.html")

@app.route("/contacto/<int:codigo>", methods=["DELETE"])
def eliminar_usuario(codigo):

  if request.method == 'DELETE':
    user.eliminar_usuario(codigo);
  return render_template("administrador.html")


@app.route("/contacto/<int:codigo>", methods=["PUT"])
def modificar_usuario(codigo):

  if request.method == 'PUT':
    user.modificar_usuario(codigo,request.form.get('nombre'),request.form.get('apellido'),request.form.get('sexo'),request.form.get('fecha_nacimiento'),request.form.get('pais'),request.form.get('email'));

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