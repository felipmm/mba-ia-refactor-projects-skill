from flask import Blueprint, request, jsonify
import controllers.report_controller as report_ctrl

report_bp = Blueprint('reports', __name__)

def _handle(fn, *args, **kwargs):
    try:
        return jsonify(fn(*args, **kwargs))
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
    except (ValueError, RuntimeError) as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    return _handle(report_ctrl.summary_report)

@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    return _handle(report_ctrl.user_report, user_id)

@report_bp.route('/categories', methods=['GET'])
def get_categories():
    return _handle(report_ctrl.list_categories)

@report_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    try:
        return jsonify(report_ctrl.create_category(data)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return _handle(report_ctrl.update_category, cat_id, data)

@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    return _handle(report_ctrl.delete_category, cat_id)
