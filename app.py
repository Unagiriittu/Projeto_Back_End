from flask import Flask, request, jsonify
from usuario import Usuario, Paciente, ProfissionalSaude, Consulta, Prontuario, engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

# Inicialização da aplicação Flask e configuração do banco de dados
app = Flask(__name__)
Session = sessionmaker(bind=engine)
SECRET_KEY = "chave-secreta-do-sistema"

# Decorador para proteger rotas com autenticação JWT.
# Lê o token do cabeçalho, valida e identifica o usuário.
def token_requerido(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            bearer = request.headers["Authorization"]
            token = bearer.replace("Bearer ", "")
        if not token:
            return jsonify({"erro": "Token não fornecido"}), 401
        try:
            dados = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            session = Session()
            usuario = session.query(Usuario).filter_by(id=dados["id"]).first()
            if not usuario:
                return jsonify({"erro": "Acesso não autorizado"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido"}), 401
        return f(usuario, *args, **kwargs)
    return decorated

# Decorador para proteger rotas com autenticação JWT.
# Lê o token do cabeçalho, valida e identifica o usuário.
@app.route("/registrar", methods=["POST"])
def registrar():
    data = request.get_json()
    session = Session()
    nome = data.get("usuario")
    senha = data.get("senha")
    is_admin = data.get("is_admin", False)
    if session.query(Usuario).filter_by(nome_de_usuario=nome).first():
        return jsonify({"erro": "Usuário já existe"}), 400
    senha_hash = generate_password_hash(senha)
    novo_usuario = Usuario(nome_de_usuario=nome, senha=senha_hash, is_admin=is_admin)
    session.add(novo_usuario)
    session.commit()
    return jsonify({"mensagem": "Usuário registrado com sucesso"}), 201

# Endpoint de login que retorna um token JWT para autenticação.
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    session = Session()
    nome = data.get("usuario")
    senha = data.get("senha")
    usuario = session.query(Usuario).filter_by(nome_de_usuario=nome).first()
    if usuario and check_password_hash(usuario.senha, senha):
        token = jwt.encode({
            "id": usuario.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token}), 200
    return jsonify({"erro": "Credenciais inválidas"}), 401

# Cadastra um novo paciente no sistema.
# Espera JSON com dados como nome, CPF, nascimento, sexo, telefone, endereço.
@app.route("/paciente", methods=["POST"])
def cadastrar_paciente():
    data = request.get_json()
    session = Session()
    # Verificar se CPF já está cadastrado
    if session.query(Paciente).filter_by(cpf=data["cpf"]).first():
        return jsonify({"erro": "Paciente com este CPF já está cadastrado"}), 400
    nascimento = datetime.datetime.strptime(data.pop("data_nascimento"), "%Y-%m-%d").date()
    novo = Paciente(**data, data_nascimento=nascimento)
    session.add(novo)
    session.commit()
    return jsonify({"mensagem": "Paciente cadastrado"}), 201

# Lista todos os pacientes cadastrados no sistema.
@app.route("/pacientes", methods=["GET"])
def listar_pacientes():
    session = Session()
    pacientes = session.query(Paciente).all()
    return jsonify([{
        "id": p.id,
        "nome": p.nome,
        "cpf": p.cpf,
        "data_nascimento": p.data_nascimento.isoformat(),
        "sexo": p.sexo,
        "telefone": p.telefone,
        "endereco": p.endereco
    } for p in pacientes]), 200

# Atualiza os dados de um paciente específico.
# Passar o ID do paciente na URL e os campos desejados no corpo.
@app.route("/paciente/<int:id>", methods=["PUT"])
def atualizar_paciente(id):
    session = Session()
    paciente = session.query(Paciente).filter_by(id=id).first()
    if not paciente:
        return jsonify({"erro": "Paciente não encontrado"}), 404
    data = request.get_json()
    for campo in ["nome", "cpf", "data_nascimento", "sexo", "telefone", "endereco"]:
        if campo in data:
            if campo == "data_nascimento":
                data[campo] = datetime.datetime.strptime(data[campo], "%Y-%m-%d").date()
            setattr(paciente, campo, data[campo])
    session.commit()
    return jsonify({"mensagem": "Paciente atualizado"}), 200

# Remove um paciente do sistema a partir de seu ID.
@app.route("/paciente/<int:id>", methods=["DELETE"])
def deletar_paciente(id):
    session = Session()
    paciente = session.query(Paciente).filter_by(id=id).first()
    if not paciente:
        return jsonify({"erro": "Paciente não encontrado"}), 404
    session.delete(paciente)
    session.commit()
    return jsonify({"mensagem": "Paciente deletado"}), 200

# Cadastra um novo profissional de saúde.
# Espera JSON com nome, CRM, especialidade, telefone, email.
@app.route("/profissional", methods=["POST"])
def cadastrar_profissional():
    data = request.get_json()
    session = Session()
    novo = ProfissionalSaude(**data)
    session.add(novo)
    session.commit()
    return jsonify({"mensagem": "Profissional cadastrado"}), 201

# Lista todos os profissionais de saúde cadastrados.
@app.route("/profissionais", methods=["GET"])
def listar_profissionais():
    session = Session()
    profissionais = session.query(ProfissionalSaude).all()
    return jsonify([{
        "id": p.id,
        "nome": p.nome,
        "crm": p.crm,
        "especialidade": p.especialidade,
        "telefone": p.telefone,
        "email": p.email
    } for p in profissionais]), 200

# Atualiza os dados de um profissional de saúde.
# Passar o ID na URL e os campos desejados no corpo.
@app.route("/profissional/<int:id>", methods=["PUT"])
def atualizar_profissional(id):
    session = Session()
    profissional = session.query(ProfissionalSaude).filter_by(id=id).first()
    if not profissional:
        return jsonify({"erro": "Profissional não encontrado"}), 404
    data = request.get_json()
    for campo in ["nome", "crm", "especialidade", "telefone", "email"]:
        if campo in data:
            setattr(profissional, campo, data[campo])
    session.commit()
    return jsonify({"mensagem": "Profissional atualizado"}), 200

# Remove um profissional de saúde pelo ID.
@app.route("/profissional/<int:id>", methods=["DELETE"])
def deletar_profissional(id):
    session = Session()
    profissional = session.query(ProfissionalSaude).filter_by(id=id).first()
    if not profissional:
        return jsonify({"erro": "Profissional não encontrado"}), 404
    session.delete(profissional)
    session.commit()
    return jsonify({"mensagem": "Profissional deletado"}), 200

# Inicia o servidor Flask em modo debug.
if __name__ == "__main__":
    app.run(debug=True)
