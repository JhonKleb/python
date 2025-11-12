from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import bcrypt


app = Flask(__name__)
api = Api(app)
CORS(app)


DB_HOST = 'localhost'
DB_NAME = 'sipat'
DB_USER = 'postgres'
DB_PASS = 'root'
DB_PORT = 5432

def get_db_connection():
    # ✅ Corrigido: já define RealDictCursor globalmente
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )


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
            pat_completo = [{
                'Tombo': row['tombo'],
                'Descrição': row['descricao'],
                'Situação': row['situacao'],
                'Local': row['local']
            } for row in rows]
            return pat_completo
        return jsonify({'message': 'Nenhum patrimônio encontrado com o tombo fornecido'}), 404


class InserirObjeto(Resource):
    def post(self):
        denuncia = request.get_json()

        tombo = denuncia.get('Tombo')
        matricula = denuncia.get('Matrícula')
        descricao = denuncia.get('Descrição')
        localizacao = denuncia.get('Localização')
        
        if not tombo or not matricula or not descricao or not localizacao:
            return jsonify({"message": "Todos os campos são obrigatórios!"}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()

    

        cur.execute("""
                INSERT INTO denuncia (tombo, matricula_al, descricao, localizacao)
                VALUES (%s, %s, %s, %s)
                """,
                (tombo, matricula, descricao, localizacao))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensagem": "Denúncia registrada com sucesso!"})

class CriarConta(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('matricula', type=int, required=True)
        parser.add_argument('nome', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('senha', type=str, required=True)
        parser.add_argument('turma', type=str, required=False)
        dados = parser.parse_args()

        senha_hash = bcrypt.hashpw(dados['senha'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM aluno WHERE matricula_al = %s", (dados['matricula'],))
        if cur.fetchone():
            cur.execute(
                "UPDATE aluno SET nome = %s, email = %s, turma = %s WHERE matricula_al = %s",
                (dados['nome'], dados['email'], dados.get('turma'), dados['matricula'])
            )
            cur.execute(
                "INSERT INTO login_aluno (matricula_al, senha) VALUES (%s, %s)",
                (dados['matricula'], senha_hash)
            )
        else:
            cur.execute("SELECT * FROM servidor WHERE matricula_serv = %s", (dados['matricula'],))
            if cur.fetchone():
                cur.execute(
                    "UPDATE servidor SET nome = %s, email = %s WHERE matricula_serv = %s",
                    (dados['nome'], dados['email'], dados['matricula'])
                )
                cur.execute(
                    "INSERT INTO login_servidor (matricula_serv, senha) VALUES (%s, %s)",
                    (dados['matricula'], senha_hash)
                )
            else:
                cur.close()
                conn.close()
                return jsonify({'message': 'Matrícula não encontrada em aluno ou servidor'}), 404

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Conta criada com sucesso!', 'matricula': dados['matricula']})

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('matricula', type=int, required=True)
        parser.add_argument('senha', type=str, required=True)
        dados = parser.parse_args()

        conn = get_db_connection()
        cur = conn.cursor()

        # 🔍 Busca primeiro em aluno, depois em servidor
        cur.execute("SELECT senha FROM login_aluno WHERE matricula_al = %s", (dados['matricula'],))
        user = cur.fetchone()
        if user is None:
            cur.execute("SELECT senha FROM login_servidor WHERE matricula_serv = %s", (dados['matricula'],))
            user = cur.fetchone()

        cur.close()
        conn.close()

        # ⚙️ Verificação segura da senha
        if user:
            try:
                senha_hash = user['senha'].encode('utf-8')
                if bcrypt.checkpw(dados['senha'].encode('utf-8'), senha_hash):
                    return {'message': 'Login bem-sucedido!', 'matricula': dados['matricula']}, 200
                else:
                    return {'message': 'Matrícula ou senha incorretos'}, 401
            except ValueError:
                return {'message': 'Erro: formato de senha inválido no banco. Recrie sua conta.'}, 500

        return {'message': 'Matrícula ou senha incorretos'}, 401


       
api.add_resource(Patrimonio, '/patrimonio')
api.add_resource(FiltrarPatrimonio, '/filtpatrimonio/<int:tombo>')
api.add_resource(InserirObjeto, '/insobj')
api.add_resource(CriarConta, '/cadastro')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)