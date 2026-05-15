import logging
import re
from database import db
from models.user import User
from models.task import Task

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')

def list_users():
    users = User.query.all()
    return [{
        'id': u.id,
        'name': u.name,
        'email': u.email,
        'role': u.role,
        'active': u.active,
        'created_at': str(u.created_at),
        'task_count': len(u.tasks)
    } for u in users]

def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise LookupError('Usuário não encontrado')
    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return data

def create_user(data):
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        raise ValueError('Nome é obrigatório')
    if not email:
        raise ValueError('Email é obrigatório')
    if not password:
        raise ValueError('Senha é obrigatória')
    if not _EMAIL_RE.match(email):
        raise ValueError('Email inválido')
    if len(password) < 4:
        raise ValueError('Senha deve ter no mínimo 4 caracteres')
    if role not in ['user', 'admin', 'manager']:
        raise ValueError('Role inválido')

    if User.query.filter_by(email=email).first():
        raise ValueError('Email já cadastrado')

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    try:
        db.session.add(user)
        db.session.commit()
        logger.info("Usuário criado: %s - %s", user.id, user.name)
        return user.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao criar usuário: %s", str(e))
        raise RuntimeError('Erro ao criar usuário')

def update_user(user_id, data):
    user = User.query.get(user_id)
    if not user:
        raise LookupError('Usuário não encontrado')

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not _EMAIL_RE.match(data['email']):
            raise ValueError('Email inválido')
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            raise ValueError('Email já cadastrado')
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < 4:
            raise ValueError('Senha muito curta')
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in ['user', 'admin', 'manager']:
            raise ValueError('Role inválido')
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    try:
        db.session.commit()
        return user.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao atualizar usuário %s: %s", user_id, str(e))
        raise RuntimeError('Erro ao atualizar')

def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise LookupError('Usuário não encontrado')

    Task.query.filter_by(user_id=user_id).delete()

    try:
        db.session.delete(user)
        db.session.commit()
        logger.info("Usuário deletado: %s", user_id)
        return {'message': 'Usuário deletado com sucesso'}
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao deletar usuário %s: %s", user_id, str(e))
        raise RuntimeError('Erro ao deletar')

def get_user_tasks(user_id):
    user = User.query.get(user_id)
    if not user:
        raise LookupError('Usuário não encontrado')
    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for t in tasks:
        data = {
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'status': t.status,
            'priority': t.priority,
            'created_at': str(t.created_at),
            'due_date': str(t.due_date) if t.due_date else None,
            'overdue': t.is_overdue()
        }
        result.append(data)
    return result

def login(email, password):
    if not email or not password:
        raise ValueError('Email e senha são obrigatórios')
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise PermissionError('Credenciais inválidas')
    if not user.active:
        raise PermissionError('Usuário inativo')
    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict()
    }
