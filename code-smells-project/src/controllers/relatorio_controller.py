from models import pedido_model


def relatorio_vendas():
    dados = pedido_model.get_dados_relatorio()
    faturamento = dados["faturamento"]
    total_pedidos = dados["total_pedidos"]

    desconto = 0
    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000:
        desconto = faturamento * 0.05
    elif faturamento > 1000:
        desconto = faturamento * 0.02

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": dados["pendentes"],
        "pedidos_aprovados": dados["aprovados"],
        "pedidos_cancelados": dados["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
