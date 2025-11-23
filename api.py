from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, datetime
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

        for row in rows:
            for key, value in row.items():
                if isinstance(value, (date, datetime)):
                    row[key] = value.isoformat()

        if not rows:
            return {'message': 'Nenhum patrimônio encontrado'}, 404
        
        return {'patrimonio_completo': rows}, 200

class FiltrarPatrimonio(Resource):
    def get(self, tombo):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM patrimonio WHERE tombo = %s", (tombo,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        for row in rows:
            for key, value in row.items():
                if isinstance(value, (date, datetime)):
                    row[key] = value.isoformat()

        if rows:
            pat_completo = [{
                'Tombo': row['tombo'],
                'Descrição': row['descricao'],
                'Situação': row['situacao'],
                'Local': row['local']
            } for row in rows]
            return {'resultado': pat_completo}, 200
        
        return {'message': 'Nenhum patrimônio encontrado com o tombo fornecido'}, 404

class InserirObjeto(Resource):
    def post(self):
        denuncia = request.get_json()

        tombo = denuncia.get('Tombo')
        matricula = denuncia.get('Matrícula')
        descricao = denuncia.get('Descrição')
        setor = denuncia.get('Setor')

        if not tombo or not matricula or not descricao or not setor:
            return {"message": "Todos os campos são obrigatórios!"}, 400
        
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
                INSERT INTO denuncia (tombo, matricula_al, descricao, setor)
                VALUES (%s, %s, %s, %s)
                """,
                (tombo, matricula, descricao, setor)
        )

        conn.commit()
        cur.close()
        conn.close()

        return {"mensagem": "Denúncia registrada com sucesso!"}, 201

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
        aluno_existente = cur.fetchone()
        cur.execute("SELECT * FROM servidor WHERE matricula_serv = %s", (dados['matricula'],))
        servidor_existente = cur.fetchone()

        if aluno_existente or servidor_existente:
            return ({'message': 'Essa matrícula já está cadastrada!'}), 400

        if dados.get('turma'):
            cur.execute(
                "INSERT INTO aluno (matricula_al, nome, email, turma) VALUES (%s, %s, %s, %s)",
                (dados['matricula'], dados['nome'], dados['email'], dados['turma'])
            )
            cur.execute(
                "INSERT INTO login_aluno (matricula_al, senha) VALUES (%s, %s)",
                (dados['matricula'], senha_hash)
            )
        else:
            cur.execute(
                "INSERT INTO servidor (matricula_serv, nome, email) VALUES (%s, %s, %s)",
                (dados['matricula'], dados['nome'], dados['email'])
            )
            cur.execute(
                "INSERT INTO login_servidor (matricula_serv, senha) VALUES (%s, %s)",
                (dados['matricula'], senha_hash)
            )

        conn.commit()
        cur.close()
        conn.close()
        return ({'message': 'Conta criada com sucesso!', 'matricula': dados['matricula']}), 201

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('matricula', type=int, required=True)
        parser.add_argument('senha', type=str, required=True)
        dados = parser.parse_args()

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT senha FROM login_aluno WHERE matricula_al = %s", (dados['matricula'],))
        user = cur.fetchone()
        tipo = "aluno"

        if user is None:
            cur.execute("SELECT senha FROM login_servidor WHERE matricula_serv = %s", (dados['matricula'],))
            user = cur.fetchone()
            tipo = "servidor" if user else None

        cur.close()
        conn.close()

        if not user:
            return {'message': 'Matrícula ou senha incorretos'}, 401

        senha_salva = user['senha']

        if not isinstance(senha_salva, str) or not senha_salva.startswith("$2"):
            return {'message': 'Erro: senha inválida no banco. Recrie sua conta.'}, 500

        senha_hash = senha_salva.encode('utf-8')

        if bcrypt.checkpw(dados['senha'].encode('utf-8'), senha_hash):
            return {
                'message': 'Login bem-sucedido!',
                'matricula': dados['matricula'],
                'tipo': tipo
            }, 200

        return {'message': 'Matrícula ou senha incorretos'}, 401

#Classes atualizadas
class VerDenuncias(Resource):
    def get(self):
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM denuncia;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        for row in rows:
            for key, value in row.items():
                if isinstance(value, (date, datetime)):
                    row[key] = value.isoformat()

        if not rows:
            return {'message': 'Nenhuma denúncia encontrada'}, 404
        
        return {'Todas as denúncias': rows}, 200

class AdicionarSetor(Resource):
    def post(self):
        add_setor = request.get_json()

        setor = add_setor.get('Setor')
        
        if not setor:
            return ({"message": "É obrigatório adicionar o setor!"}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
                INSERT INTO setores (nome_setor)
                VALUES (%s)
                """,
                (setor,) 
        )
        
        conn.commit()
        cur.close()
        conn.close()

        return ({"mensagem": "Setor adicionado com sucesso"}), 201

class DadosUsuario(Resource):
    def get(self, matricula):
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT nome, email, matricula_al AS matricula, 'aluno' AS tipo
            FROM aluno 
            WHERE matricula_al = %s
        """, (matricula,))
        aluno = cur.fetchone()

        if aluno:
            cur.close()
            conn.close()
            return aluno, 200

        cur.execute("""
            SELECT nome, email, matricula_serv AS matricula, 'servidor' AS tipo
            FROM servidor 
            WHERE matricula_serv = %s
        """, (matricula,))
        servidor = cur.fetchone()

        cur.close()
        conn.close()

        if servidor:
            return servidor, 200

        return {"message": "Usuário não encontrado"}, 404
    
class VerSetores(Resource):
    def get(self):
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM setores;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        for row in rows:
            for key, value in row.items():
                if isinstance(value, (date, datetime)):
                    row[key] = value.isoformat()

        if not rows:
            return {'message': 'Nenhum setor encontrado'}, 404

        return {'Setores': rows}, 200

class VerDenunciasUsuario(Resource):
    def get(self, matricula):
        try:
           
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # Buscar denúncias do usuário
            cur.execute("""
                SELECT 
                    id_denuncia,
                    tombo,
                    descricao,
                    setor,
                    status,
                    TO_CHAR(data_denuncia, 'DD/MM/YYYY HH24:MI') AS data_denuncia
                FROM denuncia
                WHERE matricula_al = %s
                ORDER BY data_denuncia DESC
            """, (matricula,))

            denuncias = cur.fetchall()

            cur.close()
            conn.close()

            return jsonify({
                "status": "sucesso",
                "denuncias": denuncias
            })

        except Exception as e:
            return jsonify({
                "status": "erro",
                "mensagem": str(e)
            })

class AdicionarEquipamento(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("tombo", type=int, required=True, help="Tombo é obrigatório")
        parser.add_argument("descricao", type=str, required=True, help="Descrição é obrigatória")
        parser.add_argument("local", type=str, required=True, help="Local é obrigatório")
        parser.add_argument("codigo", type=str, required=True, help="Código é obrigatório")
        parser.add_argument("situacao", type=str, required=True, help="Situação é obrigatória")
        args = parser.parse_args()

        tombo = args["tombo"]
        descricao = args["descricao"]
        local = args["local"]
        codigo = args["codigo"]
        situacao = args["situacao"]

        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            cur.execute("SELECT nome_setor FROM setores WHERE nome_setor = %s", (local,))
            setor_existe = cur.fetchone()

            if not setor_existe:
                return {"mensagem": "Setor informado não existe"}, 400

            cur.execute("SELECT tombo FROM patrimonio WHERE tombo = %s", (tombo,))
            if cur.fetchone():
                return {"mensagem": "Já existe um equipamento com esse tombo"}, 400

            cur.execute("SELECT codigo FROM patrimonio WHERE codigo = %s", (codigo,))
            if cur.fetchone():
                return {"mensagem": "Já existe um equipamento com esse código"}, 400

            cur.execute("""
                INSERT INTO patrimonio (tombo, descricao, situacao, local, codigo)
                VALUES (%s, %s, %s, %s, %s)
            """, (tombo, descricao, situacao, local, codigo))

            conn.commit()
            cur.close()
            conn.close()

            return {"mensagem": "Equipamento adicionado com sucesso"}, 201

        except Exception as e:
            print("Erro ao adicionar equipamento:", e)
            return {"mensagem": "Erro no servidor"}, 500


api.add_resource(Patrimonio, '/patrimonio')
api.add_resource(FiltrarPatrimonio, '/filtpatrimonio/<int:tombo>')
api.add_resource(InserirObjeto, '/insobj')
api.add_resource(CriarConta, '/cadastro')
api.add_resource(Login, '/login')
#Rotas atualizadas
api.add_resource(VerDenuncias, '/denuncias')
api.add_resource(AdicionarSetor, '/addsetor')
api.add_resource(DadosUsuario, '/dadosusuario/<int:matricula>')
api.add_resource(VerSetores, '/setores')
api.add_resource(VerDenunciasUsuario, "/denuncias_usuario/<int:matricula>")
api.add_resource(AdicionarEquipamento, "/addequipamento")

if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)