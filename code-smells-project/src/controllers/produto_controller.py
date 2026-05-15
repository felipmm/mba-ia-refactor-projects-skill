import logging
from models import produto_model

logger = logging.getLogger(__name__)

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]


def listar_produtos():
    return produto_model.get_todos_produtos()


def buscar_produto(produto_id):
    return produto_model.get_produto_por_id(produto_id)


def criar_produto(dados):
    nome = dados.get("nome", "")
    descricao = dados.get("descricao", "")
    preco = dados.get("preco")
    estoque = dados.get("estoque")
    categoria = dados.get("categoria", "geral")

    if not nome or preco is None or estoque is None:
        raise ValueError("Nome, preço e estoque são obrigatórios")
    if preco < 0:
        raise ValueError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValueError("Estoque não pode ser negativo")
    if len(nome) < 2:
        raise ValueError("Nome muito curto")
    if len(nome) > 200:
        raise ValueError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValueError(f"Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}")

    novo_id = produto_model.criar_produto(nome, descricao, preco, estoque, categoria)
    logger.info("Produto criado com ID: %s", novo_id)
    return {"id": novo_id}


def atualizar_produto(produto_id, dados):
    if not produto_model.get_produto_por_id(produto_id):
        return None

    nome = dados.get("nome", "")
    descricao = dados.get("descricao", "")
    preco = dados.get("preco")
    estoque = dados.get("estoque")
    categoria = dados.get("categoria", "geral")

    if not nome or preco is None or estoque is None:
        raise ValueError("Nome, preço e estoque são obrigatórios")
    if preco < 0:
        raise ValueError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValueError("Estoque não pode ser negativo")

    produto_model.atualizar_produto(produto_id, nome, descricao, preco, estoque, categoria)
    return True


def deletar_produto(produto_id):
    if not produto_model.get_produto_por_id(produto_id):
        return None
    produto_model.deletar_produto(produto_id)
    logger.info("Produto %s deletado", produto_id)
    return True


def buscar_produtos(termo, categoria=None, preco_min=None, preco_max=None):
    return produto_model.buscar_produtos(termo, categoria, preco_min, preco_max)
