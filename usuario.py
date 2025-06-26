from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey, Text
from sqlalchemy.orm import declarative_base

# Configurações básicas do SQLAlchemy: criação de engine e base de dados
DATABASE_URL = "sqlite:///./login.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Classe de usuário do sistema. Pode ser um administrador ou um profissional.
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nome_de_usuario = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

# Classe para armazenar dados dos pacientes.
class Paciente(Base):
    __tablename__ = "pacientes"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    sexo = Column(String, nullable=False)
    telefone = Column(String)
    endereco = Column(String)

# Classe que representa profissionais de saúde, como médicos.
class ProfissionalSaude(Base):
    __tablename__ = "profissionais"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    crm = Column(String, unique=True, nullable=False)
    especialidade = Column(String)
    telefone = Column(String)
    email = Column(String)

# Classe de consultas médicas, vinculando paciente e profissional com data e hora.
class Consulta(Base):
    __tablename__ = "consultas"
    id = Column(Integer, primary_key=True)
    id_paciente = Column(Integer, ForeignKey('pacientes.id'), nullable=False)
    id_profissional = Column(Integer, ForeignKey('profissionais.id'), nullable=False)
    data = Column(Date, nullable=False)
    hora = Column(String, nullable=False)
    motivo = Column(String)

# Classe de prontuário médico, vinculada diretamente a uma consulta.
class Prontuario(Base):
    __tablename__ = "prontuarios"
    id = Column(Integer, primary_key=True)
    id_consulta = Column(Integer, ForeignKey('consultas.id'), nullable=False)
    anotacoes = Column(Text, nullable=False)

# Criação automática das tabelas no banco de dados, caso ainda não existam.
Base.metadata.create_all(engine)
