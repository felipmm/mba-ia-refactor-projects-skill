from flask import Blueprint, request, jsonify
import controllers.user_controller as user_ctrl

user_bp = Blueprint('users', __name__)

def _handle(fn, *args, **kwargs):
    try:
        return jsonify(fn(*args, **kwargs))
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
    except (ValueError, PermissionError) as e:
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users', methods=['GET'])
def get_users():
    return _handle(user_ctrl.list_users)

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return _handle(user_ctrl.get_user, user_id)

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return _handle(user_ctrl.create_user, data), 201

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return _handle(user_ctrl.update_user, user_id, data)

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    return _handle(user_ctrl.delete_user, user_id)

@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    return _handle(user_ctrl.get_user_tasks, user_id)

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    email = data.get('email')
    password = data.get('password')
    try:
        result = user_ctrl.login(email, password)
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({'error': str(e)}), 401
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
