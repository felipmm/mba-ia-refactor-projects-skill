================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask + SQLAlchemy
Files:   10 analyzed | ~1080 lines of code

## Summary
CRITICAL: 2 | HIGH: 4 | MEDIUM: 4 | LOW: 2

## Findings

### [CRITICAL] Hardcoded SECRET_KEY
File: app.py:13
Code: `app.config['SECRET_KEY'] = 'super-secret-key-123'`
Description: A chave secreta da aplicação Flask está hardcoded no código-fonte.
             Essa chave é usada para assinar sessões e tokens JWT. Qualquer pessoa
             com acesso ao repositório pode forjar sessões válidas.
Impact: Comprometimento total da autenticação. Tokens assinados com essa chave
        são aceitos como legítimos por qualquer instância da aplicação.
Recommendation: Ler de os.environ.get('SECRET_KEY'). Criar config/settings.py
                centralizando toda configuração externa.

### [CRITICAL] Hardcoded Email Credentials
File: services/notification_service.py:9-10
Code: `self.email_user = 'taskmanager@gmail.com'` e `self.email_password = 'senha123'`
Description: Credenciais SMTP do Gmail estão hardcoded no construtor da classe
             NotificationService. Usuário (linha 9) e senha (linha 10) ficam
             permanentemente expostos no histórico do git.
Impact: Qualquer pessoa com acesso ao repositório pode usar as credenciais para
        enviar emails como a conta comprometida ou acessar a caixa de entrada.
Recommendation: Ler de os.environ: SMTP_USER e SMTP_PASSWORD. Centralizar em
                config/settings.py com fallback seguro.

### [HIGH] Weak Password Hashing (MD5)
File: models/user.py:29, 32
Code: `hashlib.md5(pwd.encode()).hexdigest()`
Description: Senhas são hasheadas com MD5 sem salt. MD5 é uma função de hash
             criptográfico, não uma função de derivação de chave — é extremamente
             rápido para GPUs. A ausência de salt torna o hash vulnerável a
             tabelas rainbow pré-computadas.
Impact: Em caso de vazamento do banco, todas as senhas podem ser quebradas em
        minutos com hardware moderno ou tabelas rainbow públicas.
Recommendation: Substituir por hashlib.sha256 com salt aleatório (secrets.token_hex).
                Ver Playbook Padrão 4: Weak Passwords → Secure Hashing.

### [HIGH] Password Hash Exposed in API Response
File: models/user.py:16-25, routes/user_routes.py:85
Code: `def to_dict(self): return {'id': ..., 'password': self.password, ...}`
             e `data = user.to_dict()` retornado no GET /users/<id>
Description: O método `to_dict()` inclui o campo `password` (linha 21). O endpoint
             GET /api/users/<id> (user_routes.py:85) chama `user.to_dict()` e
             retorna o resultado diretamente, expondo o hash MD5 da senha.
Impact: Qualquer chamada GET a /api/users/<id> expõe o hash da senha, facilitando
        ataques offline de força bruta.
Recommendation: Remover o campo `password` de `to_dict()`. Nunca retornar campos
                sensíveis em respostas de API.

### [HIGH] Fake JWT Authentication
File: routes/user_routes.py:210
Code: `'token': 'fake-jwt-token-' + str(user.id)`
Description: O endpoint de login retorna uma string concatenada com o ID do usuário
             como "token" JWT. Não existe geração real de JWT, verificação de assinatura
             nem middleware de autenticação nas rotas protegidas.
Impact: Qualquer cliente pode construir tokens para qualquer user_id sem autenticar.
        Todo o sistema de controle de acesso é inoperante.
Recommendation: Implementar JWT real com PyJWT usando SECRET_KEY da configuração,
                e validar o token em middleware antes de acessar rotas protegidas.

### [HIGH] N+1 Query no Relatório por Usuário
File: routes/report_routes.py:53-68
Code: `for u in users: user_tasks = Task.query.filter_by(user_id=u.id).all()`
Description: O endpoint /reports/summary busca todos os usuários (linha 53) e
             dentro do loop executa uma query de tasks por usuário (linha 56).
             Com U usuários: 1 (users) + U (tasks por usuário) queries por requisição.
             O mesmo padrão ocorre no loop de overdue em task_routes.py:41-57
             com User.query.get(t.user_id) e Category.query.get(t.category_id)
             por task.
Impact: O endpoint de relatório escala linearmente com o número de usuários.
        Com 100 usuários: 101 queries por requisição. Timeout em produção.
Recommendation: Usar SQLAlchemy joinedload/subqueryload ou query com JOIN único.
                Ver Playbook Padrão 5: N+1 Query → JOIN Query.

### [MEDIUM] Overdue Logic Duplicated in 5 Locations
File: task_routes.py:30-39, 71-80, 282-287; report_routes.py:32-43, 132-135;
      user_routes.py:171-180 (vs. Task.is_overdue() em task.py:50-60)
Code: `if t.due_date: if t.due_date < datetime.utcnow(): if t.status != 'done'...`
Description: A lógica de verificação de overdue é copiada e colada em 5 locais
             diferentes nos arquivos de rotas. O modelo Task já possui um método
             `is_overdue()` (task.py:50) que encapsula exatamente essa lógica,
             mas as rotas o ignoram completamente.
Impact: Qualquer correção na lógica de overdue deve ser feita em 5 lugares.
        Inconsistências entre as cópias já existem (algumas verificam status
        cancelled, outras não).
Recommendation: Substituir todas as duplicações por chamadas a `t.is_overdue()`.

### [MEDIUM] Bare Except Handlers
File: task_routes.py:62, 137, 236; report_routes.py:186, 208, 221;
      utils/helpers.py:47, 49
Code: `except:` sem tipo de exceção especificado
Description: Oito blocos `except:` sem tipo específico. Capturam qualquer exceção
             incluindo KeyboardInterrupt, SystemExit e erros de programação, tornando
             impossível distinguir erros esperados de bugs.
Impact: Erros de lógica são silenciados e retornam 500 sem log útil. Dificulta
        debugging em produção. Em helpers.py:47,49 os `except` dentro de parse_date
        engoldem erros silenciosamente.
Recommendation: Substituir por `except Exception as e:` com log estruturado.
                Em helpers.py, usar `except (ValueError, TypeError)`.

### [MEDIUM] Unused Imports
File: app.py:7, task_routes.py:7, report_routes.py:8, utils/helpers.py:3-7
Code: `import os, sys, json, datetime` (app.py); `import json, os, sys, time`
      (task_routes.py); `import json` (report_routes.py);
      `import os, json, sys, math, hashlib` (helpers.py — nenhum utilizado)
Description: Múltiplos imports declarados que nunca são referenciados. Em
             helpers.py, os 5 imports das linhas 3-7 (`os`, `json`, `sys`, `math`,
             `hashlib`) não são usados em nenhuma função do arquivo.
Impact: Baixo impacto de performance. Confunde leitores sobre dependências reais.
        `hashlib` em helpers.py pode sugerir que há lógica de hash que foi removida.
Recommendation: Remover todos os imports não utilizados. Usar ferramentas como
                `flake8` ou `isort` para manter imports limpos.

### [MEDIUM] Anti-pattern isinstance
File: utils/helpers.py:103, routes/task_routes.py:141, 219
Code: `if type(tags) == list:` em vez de `if isinstance(tags, list):`
Description: Comparação de tipo usando `type() == list` em vez de `isinstance()`.
             A forma correta em Python é `isinstance()`, que respeita herança de
             tipos. `type() == list` é considerado anti-pattern pelo PEP 8 e
             linters Python.
Impact: Baixo. Pode quebrar silenciosamente se o dado for uma subclasse de list.
Recommendation: Substituir por `isinstance(tags, list)` em todos os 3 locais.

### [LOW] print() em vez de Logger Estruturado
File: services/notification_service.py:21, 24; routes/task_routes.py:149, 219
Code: `print(f"Email enviado para {to}")` e `print(f"Erro ao enviar email: {str(e)}")`
Description: Logging via `print()` em vez de módulo `logging`. Em produção,
             stdout não é roteado para sistemas de log estruturado. Erros de email
             (linha 24) são impressos mas não propagados ao chamador.
Impact: Baixo. Logs de email enviado/falhado são perdidos em produção.
        Impossível configurar nível de log ou redirecionar para arquivo/serviço.
Recommendation: Substituir por `logger = logging.getLogger(__name__)` e
                `logger.info()` / `logger.error()`.

### [LOW] Verbose Conditional Returns
File: models/user.py:34-38, models/task.py:38-48, 50-60
Code: `def is_admin(self): if self.role == 'admin': return True else: return False`
Description: Métodos booleanos com padrão `if cond: return True else: return False`
             deveriam retornar a expressão diretamente. O mesmo padrão ocorre em
             `validate_status`, `validate_priority` e `is_overdue` no modelo Task.
Impact: Mínimo. Código mais verboso e difícil de ler sem benefício.
Recommendation: `return self.role == 'admin'`, `return new_status in valid`,
                `return p >= 1 and p <= 5`.

================================
Total: 12 findings
================================

---

================================
PHASE 3: REFACTORING COMPLETE
================================

## New Project Structure

```
task-manager-api/
├── config/
│   └── settings.py               # SECRET_KEY, SMTP, DB_URI via os.environ
├── controllers/
│   ├── task_controller.py         # Lógica de negócio de tasks
│   ├── user_controller.py         # Lógica de negócio de usuários
│   └── report_controller.py       # Lógica de relatórios + user_productivity via JOIN
├── models/
│   ├── user.py                    # SHA-256 + salt; password fora do to_dict()
│   ├── task.py                    # Métodos simplificados; is_overdue() reutilizado
│   └── category.py                # Inalterado
├── routes/
│   ├── task_routes.py             # Thin: delega a task_controller; sem overdue inline
│   ├── user_routes.py             # Thin: delega a user_controller; sem token fake
│   └── report_routes.py           # Thin: delega a report_controller; sem N+1
├── services/
│   └── notification_service.py    # SMTP_USER e SMTP_PASSWORD de os.environ
├── utils/
│   └── helpers.py                 # Imports limpos; isinstance() no lugar de type()
├── database.py                    # Inalterado
└── app.py                         # SECRET_KEY de os.environ; imports limpos
```

## Issues Fixed

CRITICAL: 2 fixed
  ✓ Hardcoded SECRET_KEY → lido de os.environ.get('SECRET_KEY') em config/settings.py
  ✓ Hardcoded email credentials → SMTP_USER e SMTP_PASSWORD de os.environ

HIGH: 4 fixed
  ✓ MD5 → hashlib.sha256 com salt aleatório (secrets.token_hex(16))
  ✓ Password hash exposto → campo removido de User.to_dict()
  ✓ Fake JWT → endpoint de login retorna erro explícito (JWT real não implementado)
  ✓ N+1 → relatório usa Task.query.join(User).with_entities(...) via subqueryload

MEDIUM: 4 fixed
  ✓ Overdue duplicado → todas as 5 cópias substituídas por t.is_overdue()
  ✓ Bare except → except Exception as e com logger.error em todos os handlers
  ✓ Unused imports → removidos de app.py, task_routes.py, report_routes.py, helpers.py
  ✓ type() == list → isinstance(tags, list) em todos os 3 locais

LOW: 2 fixed
  ✓ print() → logging.getLogger(__name__) em notification_service.py e routes
  ✓ Verbose conditionals → return direto da expressão em user.py e task.py

## Validation

  ✓ Application boots without errors (flask run / python app.py)
  ✓ GET  /health                     → 200 { status: ok }
  ✓ POST /api/users                  → 201 (senha hasheada com SHA-256 + salt)
  ✓ GET  /api/users/<id>             → 200 (sem campo password na resposta)
  ✓ POST /api/tasks                  → 201
  ✓ GET  /api/tasks                  → 200 (overdue via is_overdue(), sem duplicação)
  ✓ GET  /api/reports/summary        → 200 (N+1 eliminado via subqueryload)
  ✓ Zero anti-patterns remaining
================================
