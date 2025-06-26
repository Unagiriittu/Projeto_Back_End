SGHSS - Sistema de Gestão Hospitalar e de Serviços de Saúde
Este projeto é uma API REST desenvolvida em Python usando Flask, com o objetivo de gerenciar pacientes, profissionais de saúde, consultas e prontuários eletrônicos.

Funcionalidades
Cadastro e autenticação de usuários
Cadastro de pacientes e profissionais
Registro de consultas e prontuários
Atualização e remoção de registros
Segurança com JWT
Estrutura modular usando SQLAlchemy
Como executar
Clone este repositório
Instale as dependências:
pip install -r requirements.txt
Execute o servidor:
python app.py
Testes
Use o Postman para testar os endpoints descritos na documentação. Os testes incluem:

POST /registrar
POST /login
CRUD de pacientes e profissionais
Estrutura
projeto_sghss/
├── app.py
├── usuario.py
├── login.db
├── .env
├── .gitignore
└── requirements.txt
