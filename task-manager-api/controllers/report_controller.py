from datetime import datetime, timedelta
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from sqlalchemy.orm import subqueryload

def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    overdue_tasks = Task.query.filter(
        Task.due_date.isnot(None),
        Task.due_date < datetime.utcnow(),
        Task.status.notin_(['done', 'cancelled'])
    ).all()

    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    users = User.query.options(subqueryload(User.tasks)).all()
    user_stats = []
    for u in users:
        total = len(u.tasks)
        completed = sum(1 for t in u.tasks if t.status == 'done')
        user_stats.append({
            'user_id': u.id,
            'user_name': u.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0
        })

    return {
        'generated_at': str(datetime.utcnow()),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': Task.query.filter_by(status='pending').count(),
            'in_progress': Task.query.filter_by(status='in_progress').count(),
            'done': Task.query.filter_by(status='done').count(),
            'cancelled': Task.query.filter_by(status='cancelled').count(),
        },
        'tasks_by_priority': {
            'critical': Task.query.filter_by(priority=1).count(),
            'high': Task.query.filter_by(priority=2).count(),
            'medium': Task.query.filter_by(priority=3).count(),
            'low': Task.query.filter_by(priority=4).count(),
            'minimal': Task.query.filter_by(priority=5).count(),
        },
        'overdue': {
            'count': len(overdue_tasks),
            'tasks': [{
                'id': t.id,
                'title': t.title,
                'due_date': str(t.due_date),
                'days_overdue': (datetime.utcnow() - t.due_date).days
            } for t in overdue_tasks],
        },
        'recent_activity': {
            'tasks_created_last_7_days': Task.query.filter(Task.created_at >= seven_days_ago).count(),
            'tasks_completed_last_7_days': Task.query.filter(
                Task.status == 'done',
                Task.updated_at >= seven_days_ago
            ).count(),
        },
        'user_productivity': user_stats,
    }

def user_report(user_id):
    user = User.query.get(user_id)
    if not user:
        raise LookupError('Usuário não encontrado')

    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    done = sum(1 for t in tasks if t.status == 'done')
    pending = sum(1 for t in tasks if t.status == 'pending')
    in_progress = sum(1 for t in tasks if t.status == 'in_progress')
    cancelled = sum(1 for t in tasks if t.status == 'cancelled')
    overdue = sum(1 for t in tasks if t.is_overdue())
    high_priority = sum(1 for t in tasks if t.priority <= 2)

    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
        }
    }

def list_categories():
    categories = Category.query.all()
    result = []
    for c in categories:
        cat_data = c.to_dict()
        cat_data['task_count'] = Task.query.filter_by(category_id=c.id).count()
        result.append(cat_data)
    return result

def create_category(data):
    name = data.get('name')
    if not name:
        raise ValueError('Nome é obrigatório')
    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', '#000000')
    try:
        db.session.add(category)
        db.session.commit()
        return category.to_dict()
    except Exception as e:
        db.session.rollback()
        raise RuntimeError('Erro ao criar categoria')

def update_category(cat_id, data):
    cat = Category.query.get(cat_id)
    if not cat:
        raise LookupError('Categoria não encontrada')
    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']
    try:
        db.session.commit()
        return cat.to_dict()
    except Exception as e:
        db.session.rollback()
        raise RuntimeError('Erro ao atualizar')

def delete_category(cat_id):
    cat = Category.query.get(cat_id)
    if not cat:
        raise LookupError('Categoria não encontrada')
    try:
        db.session.delete(cat)
        db.session.commit()
        return {'message': 'Categoria deletada'}
    except Exception as e:
        db.session.rollback()
        raise RuntimeError('Erro ao deletar')
