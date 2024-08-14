from flask import Blueprint, request, jsonify
from .models import Rule, Evaluation, db
from sqlalchemy import text
from .rules_engine import create_rule, combine_rules, evaluate_rule, serialize_node, deserialize_node
import json
api_bp = Blueprint('api', __name__)

@api_bp.route('/test_connection', methods=['GET'])
def test_connection():
    try:
        # Execute a simple query to check the connection
        result = db.session.execute(text('SELECT 1'))
        return jsonify({"status": "Connected to PostgreSQL!", "result": [row[0] for row in result]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/rules', methods=['POST'])
def add_rule():
    rule_string = request.json.get('rule_string')
    description = request.json.get('description')
    
    # Serialize the AST
    serialized_rule = create_rule(rule_string)
    
    new_rule = Rule(rule_string=serialized_rule, description=description)
    db.session.add(new_rule)
    db.session.commit()
    
    return jsonify({"id": new_rule.id}), 200

@api_bp.route('/rules/<int:rule_id>', methods=['GET'])
def get_rule(rule_id):
    rule = Rule.query.get(rule_id)
    if not rule:
        return jsonify({"error": "Rule not found"}), 404

    return jsonify({
        "id": rule.id,
        "rule_string": rule.rule_string,
        "description": rule.description,
    }), 200

@api_bp.route('/rules/<int:rule_id>', methods=['PUT'])
def update_rule(rule_id):
    rule = Rule.query.get(rule_id)
    if not rule:
        return jsonify({"error": "Rule not found"}), 404

    rule_string = request.json.get('rule_string')
    description = request.json.get('description')
    
    # Create the AST from the new rule_string
    # Serialize the AST
    serialized_rule = create_rule(rule_string)
    
    rule.rule_string = serialized_rule
    rule.description = description
    db.session.commit()
    
    return jsonify({"status": "success"}), 200

@api_bp.route('/rules/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    
    rule = Rule.query.get(rule_id)
    if not rule:
        return jsonify({"error": "Rule not found"}), 404
    db.session.delete(rule)
    db.session.commit()
    return jsonify({"status": "success"}), 200

@api_bp.route('/evaluate', methods=['POST'])
def evaluate_rules():
    rule_ids = request.json.get('rule_ids')
    data = request.json.get('data')
    rules = Rule.query.filter(Rule.id.in_(rule_ids)).all()
    if len(rules) == 0:
         return jsonify({"result": "RULE NOT FOUND"}), 200
    combined_ast_string = combine_rules(rules)
    result = evaluate_rule(combined_ast_string, data)
    
    new_evaluation = Evaluation(rule_id=rule_ids[0], data=json.dumps(data), result=result)
    db.session.add(new_evaluation)
    db.session.commit()
    return jsonify({"result": result}), 200
