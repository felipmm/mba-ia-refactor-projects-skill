================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~784 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 4 | LOW: 3

## Findings

### [CRITICAL] SQL Injection via String Concatenation
File: models.py:28-293
Code: `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))`
Description: 19 queries constroem SQL via concatenação de strings Python, sem
             nenhuma parametrização. Linhas afetadas: 28, 48-49, 58-60, 68, 92,
             110, 127-128, 140, 149-150, 155, 158-160, 163-165, 174, 188, 192,
             220, 224, 280, 291-293. A função `buscar_produtos` (linha 285-299)
             monta uma query dinâmica concatenando `termo`, `categoria`,
             `preco_min` e `preco_max` diretamente na string SQL.
Impact: Permite leitura, modificação ou exclusão arbitrária de dados. Um atacante
        pode fazer login com qualquer conta via: email = `' OR '1'='1`.
Recommendation: Substituir toda concatenação por queries parametrizadas com `?`.
                Ver Playbook Padrão 1: SQL Injection → Parameterized Queries.

### [CRITICAL] Hardcoded Secret Key
File: app.py:7
Code: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`
Description: A chave secreta da aplicação está hardcoded no código-fonte. O mesmo
             valor é exposto novamente no endpoint /health (controllers.py:289).
Impact: Qualquer pessoa com acesso ao repositório pode forjar tokens de sessão e
        se autenticar como qualquer usuário da aplicação.
Recommendation: Ler de variável de ambiente: `os.environ.get('SECRET_KEY')`.
                Ver Playbook Padrão 2: Hardcoded Secrets → Config Module + Env Vars.

### [CRITICAL] Dangerous Admin Endpoints Without Authentication
File: app.py:47-78
Code: `@app.route("/admin/reset-db", methods=["POST"])` e `@app.route("/admin/query", methods=["POST"])`
Description: Dois endpoints destrutivos sem nenhuma autenticação ou autorização:
             - `/admin/reset-db` (linhas 47-57): deleta TODOS os dados de todas as tabelas.
             - `/admin/query` (linhas 59-78): executa SQL arbitrário fornecido pelo
               cliente via `request.json["sql"]`, incluindo DROP TABLE, SELECT de
               dados sensíveis etc.
Impact: Qualquer pessoa com acesso à rede pode apagar todo o banco de dados ou
        executar queries maliciosas sem precisar de credenciais.
Recommendation: Remover `/admin/query` completamente — não existe forma segura de
                expor execução de SQL arbitrário. Proteger `/admin/reset-db` com
                token de administrador via middleware. Ver Playbook Padrão 10.

### [CRITICAL] Secret Key Exposed in API Response
File: controllers.py:289
Code: `"secret_key": "minha-chave-super-secreta-123"`
Description: O endpoint GET /health retorna a SECRET_KEY da aplicação no corpo
             da resposta JSON, visível para qualquer cliente que faça a requisição.
Impact: Exposição completa da chave criptográfica da aplicação via API pública.
Recommendation: Remover todos os campos de configuração sensível da resposta do
                /health. O endpoint deve retornar apenas status, versão e uptime.

### [HIGH] Plaintext Password Storage
File: database.py:76-78, models.py:110, models.py:127-128
Code: `("Admin", "admin@loja.com", "admin123", "admin")`
Description: Senhas são armazenadas em texto plano na coluna `senha` da tabela
             `usuarios`. O seed (database.py:76-78) insere senhas legíveis. O
             login (models.py:110) compara a senha fornecida diretamente com o
             valor do banco sem hash. A criação de usuário (models.py:127-128)
             persiste a senha como recebida.
Impact: Se o banco de dados for comprometido (via SQL Injection, por exemplo),
        todas as senhas dos usuários ficam expostas imediatamente.
Recommendation: Aplicar hash com salt antes de armazenar. Ver Playbook Padrão 4:
                Plaintext Passwords → Secure Hashing.

### [HIGH] N+1 Query Pattern
File: models.py:187-199, models.py:219-231
Code: `cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))`
Description: Em `get_pedidos_usuario` (linhas 177-200) e `get_todos_pedidos`
             (linhas 208-233), para cada pedido retornado pela query principal,
             são executadas mais 2 queries adicionais dentro de loops `for`:
             uma para buscar os itens do pedido (cursor2) e outra para buscar
             o nome de cada produto (cursor3). Com N pedidos, cada um com M itens,
             o total de queries é 1 + N + (N×M).
Impact: Com 100 pedidos de 5 itens cada, a API executa 601 queries por requisição.
        A aplicação torna-se inutilizável sob carga mínima.
Recommendation: Substituir pelos loops por uma query com JOIN. Ver Playbook Padrão 5.

### [HIGH] Business Logic Embedded in Model Layer
File: models.py:256-262
Code: `if faturamento > 10000: desconto = faturamento * 0.1`
Description: A função `relatorio_vendas` em models.py contém lógica de negócio
             de cálculo de desconto (magic numbers 10000, 5000, 1000 e percentuais
             0.1, 0.05, 0.02) diretamente no arquivo de acesso a dados. Models
             devem apenas acessar dados; regras de negócio pertencem ao Controller.
Impact: Regras de desconto não podem ser reutilizadas ou testadas em isolamento.
        Mudança nas regras exige alterar o arquivo de banco de dados.
Recommendation: Extrair a lógica de desconto para um método em `pedido_controller.py`.
                Ver Playbook Padrão 6: Business Logic in Routes → Extract to Controller.

### [MEDIUM] DEBUG Mode Enabled in Production Config
File: app.py:8, app.py:88
Code: `app.config["DEBUG"] = True` e `app.run(..., debug=True)`
Description: O modo debug está ativo tanto na configuração da aplicação (linha 8)
             quanto na chamada de `app.run()` (linha 88). Isso ativa o debugger
             interativo do Werkzeug e recarregamento automático.
Impact: Em produção, o debugger interativo expõe um console Python no browser
        quando ocorre um erro, permitindo execução de código arbitrário no servidor.
Recommendation: Ler de env var: `DEBUG = os.environ.get('DEBUG', 'false') == 'true'`.

### [MEDIUM] Code Duplication in Validation Logic
File: controllers.py:24-62, controllers.py:64-96
Code: `if "nome" not in dados: return jsonify({"erro": "Nome é obrigatório"}), 400`
Description: Os handlers `criar_produto` (linhas 24-62) e `atualizar_produto`
             (linhas 64-96) contêm blocos de validação quase idênticos: verificação
             de `nome`, `preco`, `estoque`, negatividade de preço e estoque. O
             código é copiado com pequenas diferenças e deve ser mantido em dois
             lugares.
Impact: Bug em validação corrigido em um lugar mas não no outro. Manutenção dobrada.
Recommendation: Extrair para uma função `_validar_dados_produto(dados)` compartilhada.
                Ver Playbook Padrão 8: Code Duplication → Extract Method.

### [MEDIUM] Bare Exception Handlers Exposing Internal Errors
File: controllers.py (múltiplas funções), app.py:77-78
Code: `except Exception as e: return jsonify({"erro": str(e)}), 500`
Description: Todos os handlers em controllers.py usam `except Exception as e` e
             retornam `str(e)` diretamente na resposta. O handler em app.py:77-78
             no endpoint `/admin/query` faz o mesmo. Isso expõe mensagens de erro
             internas do SQLite e do Python para o cliente.
Impact: Vaza informações sobre estrutura do banco, nomes de tabelas e colunas,
        e caminhos internos do servidor — facilita ataques direcionados.
Recommendation: Logar o erro internamente; retornar mensagem genérica ao cliente.
                Ver Playbook Padrão 9: Bare Exception Handlers → Specific Handlers.

### [MEDIUM] Global Mutable Connection with Thread-Safety Bypass
File: database.py:4, database.py:10
Code: `db_connection = None` e `sqlite3.connect(db_path, check_same_thread=False)`
Description: A conexão com o banco é mantida em uma variável global mutável
             (`db_connection`). O parâmetro `check_same_thread=False` desabilita
             a verificação de thread-safety do SQLite, que existe para prevenir
             corrupção de dados em acessos concorrentes.
Impact: Em ambientes com múltiplos workers ou threads, acessos concorrentes ao
        mesmo objeto de conexão podem corromper transações.
Recommendation: Usar `flask.g` para conexão por-request (padrão Flask) ou
                migrar para SQLAlchemy com pool de conexões.

### [LOW] Mock Notification Implementation via print()
File: controllers.py:208-210, controllers.py:248-250
Code: `print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " criado...")`
Description: As notificações de criação e atualização de pedido são implementadas
             como `print()` no console, sem nenhuma integração real com email,
             SMS ou push notification.
Impact: Usuários nunca recebem notificações. Logs de produção ficam poluídos com
        mensagens de debug.
Recommendation: Criar um `notification_service.py` com implementação real ou
                registrar via `logging.info()` como placeholder documentado.

### [LOW] Hardcoded Valid Categories List
File: controllers.py:52
Code: `categorias_validas = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]`
Description: A lista de categorias válidas está hardcoded dentro da função
             `criar_produto`. Se categorias forem adicionadas ou removidas,
             é necessário modificar o código.
Impact: Baixo. Manutenção manual desnecessária.
Recommendation: Mover para `config/settings.py` como constante `CATEGORIAS_VALIDAS`.

### [LOW] Password Exposed in GET /usuarios Response
File: models.py:83, models.py:99
Code: `"senha": row["senha"]`
Description: As funções `get_todos_usuarios` e `get_usuario_por_id` incluem o
             campo `senha` na resposta serializada, expondo as senhas (em texto
             plano) via GET /usuarios e GET /usuarios/<id>.
Impact: Qualquer cliente da API consegue listar as senhas de todos os usuários
        com uma simples requisição GET.
Recommendation: Remover o campo `senha` da serialização nos models ou criar um
                método `to_dict()` que exclua explicitamente campos sensíveis.

================================
Total: 14 findings
================================

---

================================
PHASE 3: REFACTORING COMPLETE
================================

## New Project Structure

```
src/
├── config/
│   └── settings.py          # Config via os.environ, sem hardcode
├── models/
│   ├── produto_model.py     # Queries parametrizadas para produtos
│   ├── usuario_model.py     # Sem expor senha; sem hash na API
│   └── pedido_model.py      # JOIN único substitui N+1 queries
├── controllers/
│   ├── produto_controller.py    # Validação centralizada (sem duplicação)
│   ├── usuario_controller.py    # Hash/verify de senha aqui
│   ├── pedido_controller.py     # Notificações via logger
│   └── relatorio_controller.py  # Lógica de desconto isolada
├── views/
│   └── routes.py            # Só roteamento, sem lógica de negócio
├── middlewares/
│   └── error_handler.py     # Erros centralizados, sem vazar detalhes
├── utils/
│   └── security.py          # hash_password / verify_password (SHA-256 + salt)
├── database.py              # get_db() via flask.g, close_db() no teardown
└── app.py                   # create_app() factory + if __name__ == '__main__'
```

## Issues Fixed

CRITICAL: 4 fixed
  ✓ SQL Injection → todas as 19 queries agora usam placeholders (?)
  ✓ Hardcoded SECRET_KEY → lida de os.environ.get('SECRET_KEY')
  ✓ /admin/query removido completamente (404)
  ✓ /admin/reset-db protegido por X-Admin-Token header
  ✓ Secret key removida do /health response

HIGH: 3 fixed
  ✓ Plaintext passwords → SHA-256 com salt (sem dependência externa)
  ✓ N+1 queries → substituídas por JOIN único em pedido_model.py
  ✓ Business logic → lógica de desconto em relatorio_controller.py

MEDIUM: 4 fixed
  ✓ DEBUG mode → controlado por env var DEBUG
  ✓ Code duplication → validação de produto unificada no controller
  ✓ Bare exceptions → logger.exception + erros específicos
  ✓ Global connection → flask.g com teardown_appcontext

LOW: 3 fixed
  ✓ print() notifications → logger.info()
  ✓ Hardcoded categories list → constante em config/settings.py
  ✓ Senha exposta em GET /usuarios → _to_dict_public() exclui campo senha

## Validation

  ✓ Application boots without errors
  ✓ GET /                      → 200 OK
  ✓ GET /produtos               → 200 OK (10 produtos)
  ✓ POST /produtos              → 201 Created
  ✓ POST /login                 → 200 OK (senha hasheada validada)
  ✓ POST /pedidos               → 201 Created
  ✓ GET /relatorios/vendas      → 200 OK (lógica de desconto correta)
  ✓ GET /health                 → 200 OK (sem secret_key, sem debug)
  ✓ POST /admin/reset-db sem token → 401 Unauthorized
  ✓ POST /admin/query           → 404 Not Found (endpoint removido)
  ✓ Zero anti-patterns remaining
================================
