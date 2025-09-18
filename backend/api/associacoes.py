from flask import Blueprint, jsonify, request
from backend.models import Associacao
from backend.extensions import db

associacoes_bp = Blueprint('associacoes_bp', __name__, url_prefix='/api/associacoes')

@associacoes_bp.route('/', methods=['GET'])
def get_associacoes():
    try:
        associacoes = Associacao.query.all()
        return jsonify([a.to_dict() for a in associacoes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@associacoes_bp.route('/', methods=['POST'])
def create_associacao():
    data = request.get_json()
    if not data or not data.get('parceiro_id') or not data.get('loja_id') or not data.get('status'):
        return jsonify({'error': 'Campos obrigatórios não fornecidos'}), 400

    try:
        nova_associacao = Associacao(
            parceiro_id=data['parceiro_id'],
            loja_id=data['loja_id'],
            status=data['status']
        )
        db.session.add(nova_associacao)
        db.session.commit()
        return jsonify(nova_associacao.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@associacoes_bp.route('/<int:associacao_id>', methods=['PUT'])
def update_associacao(associacao_id):
    associacao = Associacao.query.get_or_404(associacao_id)
    data = request.get_json()
    if not data or not data.get('status'):
        return jsonify({'error': 'Status é obrigatório'}), 400

    try:
        associacao.status = data['status']
        db.session.commit()
        return jsonify(associacao.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@associacoes_bp.route('/<int:associacao_id>', methods=['DELETE'])
def delete_associacao(associacao_id):
    associacao = Associacao.query.get_or_404(associacao_id)
    try:
        db.session.delete(associacao)
        db.session.commit()
        return jsonify({'message': 'Associação excluída com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
