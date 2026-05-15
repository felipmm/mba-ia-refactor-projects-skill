import logging
from models import pedido_model

logger = logging.getLogger(__name__)

STATUSES_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


def criar_pedido(usuario_id, itens):
    resultado = pedido_model.criar_pedido(usuario_id, itens)
    if "erro" in resultado:
        return resultado
    _notificar_novo_pedido(resultado["pedido_id"])
    logger.info("Pedido %s criado para usuario %s", resultado["pedido_id"], usuario_id)
    return resultado


def listar_todos_pedidos():
    return pedido_model.get_todos_pedidos()


def listar_pedidos_usuario(usuario_id):
    return pedido_model.get_pedidos_usuario(usuario_id)


def atualizar_status_pedido(pedido_id, novo_status):
    if novo_status not in STATUSES_VALIDOS:
        raise ValueError("Status inválido")
    pedido_model.atualizar_status_pedido(pedido_id, novo_status)
    _notificar_mudanca_status(pedido_id, novo_status)


def _notificar_novo_pedido(pedido_id):
    logger.info("NOTIFICAÇÃO EMAIL: Pedido %s criado", pedido_id)
    logger.info("NOTIFICAÇÃO SMS: Seu pedido foi recebido!")
    logger.info("NOTIFICAÇÃO PUSH: Novo pedido recebido pelo sistema")


def _notificar_mudanca_status(pedido_id, status):
    if status == "aprovado":
        logger.info("NOTIFICAÇÃO: Pedido %s aprovado! Preparar envio.", pedido_id)
    elif status == "cancelado":
        logger.info("NOTIFICAÇÃO: Pedido %s cancelado. Devolver estoque.", pedido_id)
