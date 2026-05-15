import logging
from models import usuario_model
from utils import hash_password, verify_password

logger = logging.getLogger(__name__)


def listar_usuarios():
    return usuario_model.get_todos_usuarios()


def buscar_usuario(usuario_id):
    return usuario_model.get_usuario_por_id(usuario_id)


def criar_usuario(nome, email, senha):
    senha_hash = hash_password(senha)
    novo_id = usuario_model.criar_usuario(nome, email, senha_hash)
    logger.info("Usuário criado: %s", email)
    return {"id": novo_id}


def login(email, senha):
    row = usuario_model.get_usuario_por_email(email)
    if not row:
        logger.info("Login falhou (usuário não encontrado): %s", email)
        return None
    if not verify_password(row["senha"], senha):
        logger.info("Login falhou (senha incorreta): %s", email)
        return None
    logger.info("Login bem-sucedido: %s", email)
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
    }
