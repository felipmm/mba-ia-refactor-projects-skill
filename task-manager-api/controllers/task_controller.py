import logging
from datetime import datetime
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)

def list_tasks():
    tasks = Task.query.options(
        joinedload(Task.user),
        joinedload(Task.category)
    ).all()
    result = []
    for t in tasks:
        data = t.to_dict()
        data['overdue'] = t.is_overdue()
        data['user_name'] = t.user.name if t.user else None
        data['category_name'] = t.category.name if t.category else None
        result.append(data)
    return result

def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        raise LookupError('Task não encontrada')
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return data

def create_task(data):
    title = data.get('title', '').strip()
    if not title:
        raise ValueError('Título é obrigatório')
    if len(title) < 3:
        raise ValueError('Título muito curto')
    if len(title) > 200:
        raise ValueError('Título muito longo')

    status = data.get('status', 'pending')
    if status not in ['pending', 'in_progress', 'done', 'cancelled']:
        raise ValueError('Status inválido')

    try:
        priority = int(data.get('priority', 3))
    except (TypeError, ValueError):
        raise ValueError('Prioridade inválida')
    if not (1 <= priority <= 5):
        raise ValueError('Prioridade deve ser entre 1 e 5')

    user_id = data.get('user_id')
    if user_id and not User.query.get(user_id):
        raise LookupError('Usuário não encontrado')

    category_id = data.get('category_id')
    if category_id and not Category.query.get(category_id):
        raise LookupError('Categoria não encontrada')

    task = Task()
    task.title = title
    task.description = data.get('description', '')
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    due_date = data.get('due_date')
    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except (ValueError, TypeError):
            raise ValueError('Formato de data inválido. Use YYYY-MM-DD')

    tags = data.get('tags')
    if tags is not None:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    try:
        db.session.add(task)
        db.session.commit()
        logger.info("Task criada: %s - %s", task.id, task.title)
        return task.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao criar task: %s", str(e))
        raise RuntimeError('Erro ao criar task')

def update_task(task_id, data):
    task = Task.query.get(task_id)
    if not task:
        raise LookupError('Task não encontrada')

    if 'title' in data:
        title = data['title']
        if len(title) < 3:
            raise ValueError('Título muito curto')
        if len(title) > 200:
            raise ValueError('Título muito longo')
        task.title = title

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in ['pending', 'in_progress', 'done', 'cancelled']:
            raise ValueError('Status inválido')
        task.status = data['status']

    if 'priority' in data:
        if not (1 <= data['priority'] <= 5):
            raise ValueError('Prioridade deve ser entre 1 e 5')
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id'] and not User.query.get(data['user_id']):
            raise LookupError('Usuário não encontrado')
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not Category.query.get(data['category_id']):
            raise LookupError('Categoria não encontrada')
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except (ValueError, TypeError):
                raise ValueError('Formato de data inválido')
        else:
            task.due_date = None

    if 'tags' in data:
        tags = data['tags']
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    task.updated_at = datetime.utcnow()

    try:
        db.session.commit()
        logger.info("Task atualizada: %s", task.id)
        return task.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao atualizar task: %s", str(e))
        raise RuntimeError('Erro ao atualizar')

def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        raise LookupError('Task não encontrada')
    try:
        db.session.delete(task)
        db.session.commit()
        logger.info("Task deletada: %s", task_id)
        return {'message': 'Task deletada com sucesso'}
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao deletar task %s: %s", task_id, str(e))
        raise RuntimeError('Erro ao deletar')

def search_tasks(query='', status='', priority='', user_id=''):
    q = Task.query
    if query:
        q = q.filter(db.or_(
            Task.title.like(f'%{query}%'),
            Task.description.like(f'%{query}%')
        ))
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == int(priority))
    if user_id:
        q = q.filter(Task.user_id == int(user_id))
    return [t.to_dict() for t in q.all()]

def task_stats():
    total = Task.query.count()
    overdue_count = Task.query.filter(
        Task.due_date.isnot(None),
        Task.due_date < datetime.utcnow(),
        Task.status.notin_(['done', 'cancelled'])
    ).count()
    return {
        'total': total,
        'pending': Task.query.filter_by(status='pending').count(),
        'in_progress': Task.query.filter_by(status='in_progress').count(),
        'done': Task.query.filter_by(status='done').count(),
        'cancelled': Task.query.filter_by(status='cancelled').count(),
        'overdue': overdue_count,
        'completion_rate': round((Task.query.filter_by(status='done').count() / total) * 100, 2) if total > 0 else 0
    }
