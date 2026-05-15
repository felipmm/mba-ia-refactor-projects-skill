from flask import Blueprint, request, jsonify
import controllers.task_controller as task_ctrl

task_bp = Blueprint('tasks', __name__)

def _handle(fn, *args, **kwargs):
    try:
        return jsonify(fn(*args, **kwargs))
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return _handle(task_ctrl.list_tasks)

@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    return _handle(task_ctrl.get_task, task_id)

@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return _handle(task_ctrl.create_task, data), 201

@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return _handle(task_ctrl.update_task, task_id, data)

@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    return _handle(task_ctrl.delete_task, task_id)

@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    return _handle(
        task_ctrl.search_tasks,
        request.args.get('q', ''),
        request.args.get('status', ''),
        request.args.get('priority', ''),
        request.args.get('user_id', '')
    )

@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    return _handle(task_ctrl.task_stats)
