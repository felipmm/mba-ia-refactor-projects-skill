import logging
import os
from flask import jsonify, request
from database import get_db
from controllers import produto_controller, usuario_controller, pedido_controller, relatorio_controller

logger = logging.getLogger(__name__)


def register_routes(app):

    @app.route("/")
    def index():
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        })

    # ── Produtos ──────────────────────────────────────────────────────────────

    @app.route("/produtos", methods=["GET"])
    def listar_produtos():
        return jsonify({"dados": produto_controller.listar_produtos(), "sucesso": True}), 200

    @app.route("/produtos/busca", methods=["GET"])
    def buscar_produtos():
        try:
            termo = request.args.get("q", "")
            categoria = request.args.get("categoria")
            preco_min = float(request.args["preco_min"]) if request.args.get("preco_min") else None
            preco_max = float(request.args["preco_max"]) if request.args.get("preco_max") else None
            resultados = produto_controller.buscar_produtos(termo, categoria, preco_min, preco_max)
            return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
        except Exception:
            logger.exception("Erro ao buscar produtos")
            return jsonify({"erro": "Erro interno"}), 500

    @app.route("/produtos/<int:produto_id>", methods=["GET"])
    def buscar_produto(produto_id):
        produto = produto_controller.buscar_produto(produto_id)
        if produto:
            return jsonify({"dados": produto, "sucesso": True}), 200
        return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404

    @app.route("/produtos", methods=["POST"])
    def criar_produto():
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400
        try:
            resultado = produto_controller.criar_produto(dados)
            return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Produto criado"}), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400
        except Exception:
            logger.exception("Erro ao criar produto")
            return jsonify({"erro": "Erro interno"}), 500

    @app.route("/produtos/<int:produto_id>", methods=["PUT"])
    def atualizar_produto(produto_id):
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400
        try:
            resultado = produto_controller.atualizar_produto(produto_id, dados)
            if resultado is None:
                return jsonify({"erro": "Produto não encontrado"}), 404
            return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400
        except Exception:
            logger.exception("Erro ao atualizar produto")
            return jsonify({"erro": "Erro interno"}), 500

    @app.route("/produtos/<int:produto_id>", methods=["DELETE"])
    def deletar_produto(produto_id):
        try:
            resultado = produto_controller.deletar_produto(produto_id)
            if resultado is None:
                return jsonify({"erro": "Produto não encontrado"}), 404
            return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
        except Exception:
            logger.exception("Erro ao deletar produto")
            return jsonify({"erro": "Erro interno"}), 500

    # ── Usuários ──────────────────────────────────────────────────────────────

    @app.route("/usuarios", methods=["GET"])
    def listar_usuarios():
        return jsonify({"dados": usuario_controller.listar_usuarios(), "sucesso": True}), 200

    @app.route("/usuarios/<int:usuario_id>", methods=["GET"])
    def buscar_usuario(usuario_id):
        usuario = usuario_controller.buscar_usuario(usuario_id)
        if usuario:
            return jsonify({"dados": usuario, "sucesso": True}), 200
        return jsonify({"erro": "Usuário não encontrado"}), 404

    @app.route("/usuarios", methods=["POST"])
    def criar_usuario():
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400
        nome = dados.get("nome", "")
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not nome or not email or not senha:
            return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400
        try:
            resultado = usuario_controller.criar_usuario(nome, email, senha)
            return jsonify({"dados": resultado, "sucesso": True}), 201
        except Exception:
            logger.exception("Erro ao criar usuário")
            return jsonify({"erro": "Erro interno"}), 500

    @app.route("/login", methods=["POST"])
    def login():
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not email or not senha:
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400
        try:
            usuario = usuario_controller.login(email, senha)
            if usuario:
                return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
            return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
        except Exception:
            logger.exception("Erro no login")
            return jsonify({"erro": "Erro interno"}), 500

    # ── Pedidos ───────────────────────────────────────────────────────────────

    @app.route("/pedidos", methods=["POST"])
    def criar_pedido():
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400
        usuario_id = dados.get("usuario_id")
        itens = dados.get("itens", [])
        if not usuario_id:
            return jsonify({"erro": "Usuario ID é obrigatório"}), 400
        if not itens:
            return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400
        try:
            resultado = pedido_controller.criar_pedido(usuario_id, itens)
            if "erro" in resultado:
                return jsonify({"erro": resultado["erro"], "sucesso": False}), 400
            return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201
        except Exception:
            logger.exception("Erro ao criar pedido")
            return jsonify({"erro": "Erro interno"}), 500

    @app.route("/pedidos", methods=["GET"])
    def listar_todos_pedidos():
        try:
            return jsonify({"dados": pedido_controller.listar_todos_pedidos(), "sucesso": True}), 200
        except Exception:
            logger.exception("Erro ao listar pedidos")
            return jsonify({"erro": "Erro interno"}), 500

    @app.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
    def listar_pedidos_usuario(usuario_id):
        try:
            return jsonify({"dados": pedido_controller.listar_pedidos_usuario(usuario_id), "sucesso": True}), 200
        except Exception:
            logger.exception("Erro ao listar pedidos do usuário")
            return jsonify({"erro": "Erro interno"}), 500

    @app.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
    def atualizar_status_pedido(pedido_id):
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400
        novo_status = dados.get("status", "")
        try:
            pedido_controller.atualizar_status_pedido(pedido_id, novo_status)
            return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400
        except Exception:
            logger.exception("Erro ao atualizar status")
            return jsonify({"erro": "Erro interno"}), 500

    # ── Relatórios ────────────────────────────────────────────────────────────

    @app.route("/relatorios/vendas", methods=["GET"])
    def relatorio_vendas():
        try:
            return jsonify({"dados": relatorio_controller.relatorio_vendas(), "sucesso": True}), 200
        except Exception:
            logger.exception("Erro ao gerar relatório")
            return jsonify({"erro": "Erro interno"}), 500

    # ── Health ────────────────────────────────────────────────────────────────

    @app.route("/health", methods=["GET"])
    def health_check():
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            cursor.execute("SELECT COUNT(*) FROM produtos")
            produtos = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            usuarios = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM pedidos")
            pedidos = cursor.fetchone()[0]
            return jsonify({
                "status": "ok",
                "database": "connected",
                "counts": {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos},
                "versao": "1.0.0",
            }), 200
        except Exception:
            logger.exception("Health check falhou")
            return jsonify({"status": "erro"}), 500

    # ── Admin (token-protected) ───────────────────────────────────────────────

    @app.route("/admin/reset-db", methods=["POST"])
    def reset_database():
        token = request.headers.get("X-Admin-Token", "")
        admin_token = os.environ.get("ADMIN_TOKEN", "")
        if not admin_token or token != admin_token:
            return jsonify({"erro": "Não autorizado"}), 401
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM itens_pedido")
        cursor.execute("DELETE FROM pedidos")
        cursor.execute("DELETE FROM produtos")
        cursor.execute("DELETE FROM usuarios")
        db.commit()
        logger.warning("BANCO DE DADOS RESETADO")
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
