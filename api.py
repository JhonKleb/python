from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import secrets, string


app = Flask(__name__)
api = Api(app)
CORS(app)
# Configuração do MySQL
DB_HOST = 'localhost'
DB_NAME = 'sipat'
DB_USER = 'postgres'
DB_PASS = 'root'
DB_PORT = 5432

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )
    return conn

class Patrimonio(Resource):
    def get(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM patrimonio;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify({'Patrimonio completo': rows})

    
class FiltrarPatrimonio(Resource):
    def get(self, tombo):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM patrimonio WHERE tombo = %s", (tombo,))
        rows = cur.fetchall()
        conn.close()

        if rows:
            pat_completo = [{'Tombo' : row['tombo'], 'Descrição' : row['descricao'], 'Situação' : row['situacao'], 'Local': row['localizacao']} for row in rows]
            return pat_completo
        
        return jsonify({'message' : 'Nenhum patrimônio encontrado com o tombo fornecido'}), 404

class InserirObjeto(Resource):
    @staticmethod    
    def codigo(tamanho=8):
        caracters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(caracters) for _ in range(tamanho))
    
    def post(self):
        objeto = reqparse.RequestParser()
        objeto.add_argument('Tombo', type=int, required=True, help="O campo 'Tombo' é obrigatório.")
        objeto.add_argument('Matrícula', type=int, required=True, help="O campo 'Matrícula' é obrigatório.")
        objeto.add_argument('Descrição', type=str, required=True, help="O campo 'Descrição' é obrigatório.")
        objeto.add_argument('Localização', type=str, help="O campo 'Localização' é obrigatório")

        dados = objeto.parse_args()
        codigo = self.codigo()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO patrimonio (tombo, matricula, descricao, localizacao, codigo) VALUES (%s, %s, %s, %s, %s)",
            (dados['Tombo'], dados['Matrícula'], dados['Descrição'], dados['Localização'], codigo)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Objeto adicionado!', 'dados': dados, 'codigo': codigo})

class CriarConta(Resource):
    def post(self):
        objeto = reqparse.RequestParser()
        objeto.add_argument('')

#class Login(Resource):

api.add_resource(Patrimonio, '/patrimonio')
api.add_resource(FiltrarPatrimonio, '/filtpatrimonio/<int:tombo>')
api.add_resource(InserirObjeto, '/insobj')
#api.add_resource(CriarConta, '/cadastro')
#api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)    