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
        cur.execute("SELECT * FROM bd_servidor;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify({'Patrimonio completo': rows})

    
class FiltrarPatrimonio(Resource):
    def get(self, Tombo):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT Tombo, Nome,  Matricula_Serv, Situacao, Data, Local FROM BD_Servidor WHERE Tombo = %s", (Tombo,))
        rows = conn.cursor()
        cur.close()

        if rows:
            pat_completo = [{'Tombo' : row[0], 'Nome' : row[1], 'Matricula_Serv' : row[2], 'Situacao' : row[3], 'Data': row[4].strftime('%Y-%m-%d %H:%M:%S'), 'Local': row[5]} for row in rows]
            return pat_completo
        
        return jsonify({'message' : 'Nenhum patrimônio encontrado com o tombo fornecido'}), 404

class InserirObjeto(Resource):
    @staticmethod
    def data_valida(valor):
        try:
            return datetime.strptime(valor, '%d-%m-%Y').date()
        except ValueError:
            raise ValueError("Data deve estar no formato DD-MM-YYYY.")
    
    def codigo(tamanho=8):
        caracters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(caracters) for _ in range(tamanho))
    
    def post(self):
        objeto = reqparse.RequestParser()
        objeto.add_argument('Tombo', type=int, required=True, help="O campo 'Tombo' é obrigatório.")
        objeto.add_argument('Situação', type=str, required=True, help="O campo 'Situação' é obrigatório.")
        objeto.add_argument('Data', type=InserirObjeto.data_valida, required=True, help="O campo 'Data' é obrigatório e deve estar no formato DD-MM-YYYY.")
        objeto.add_argument('Local', type=str, help="O campo 'Local é obrigatório")

        dados = objeto.parse_args()
        codigo = self.codigo

        return jsonify({'message': 'Objeto adicionado!', 'dados': dados, 'codigo': codigo})

api.add_resource(Patrimonio, '/patrimonio')
api.add_resource(FiltrarPatrimonio, '/filtpatrimonio/<int:Tombo>')
api.add_resource(InserirObjeto, '/insobj')

if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)    