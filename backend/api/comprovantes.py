from flask import Blueprint, jsonify, request
from backend.models import Comprovante
from backend.extensions import db
from datetime import datetime

comprovantes_bp = Blueprint('comprovantes_bp', __name__, url_prefix='/api/comprovantes')

@comprovantes_bp.route('/', methods=['GET'])
def get_comprovantes():
    try:
        comprovantes = Comprovante.query.all()
        return jsonify([c.to_dict() for c in comprovantes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@comprovantes_bp.route('/', methods=['POST'])
def create_comprovante():
    data = request.get_json()
    if not data or not data.get('parceiro_id') or not data.get('loja_id') or not data.get('data_entrega'):
        return jsonify({'error': 'Campos obrigatórios não fornecidos'}), 400

    try:
        novo_comprovante = Comprovante(
            parceiro_id=data['parceiro_id'],
            loja_id=data['loja_id'],
            data_entrega=datetime.fromisoformat(data['data_entrega']),
            arquivo_comprovante=data.get('arquivo_comprovante', 'path/to/placeholder.pdf'), # Placeholder for now
            observacoes=data.get('observacoes')
        )
        db.session.add(novo_comprovante)
        db.session.commit()
        return jsonify(novo_comprovante.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@comprovantes_bp.route('/<int:comprovante_id>', methods=['DELETE'])
def delete_comprovante(comprovante_id):
    comprovante = Comprovante.query.get_or_404(comprovante_id)
    try:
        db.session.delete(comprovante)
        db.session.commit()
        return jsonify({'message': 'Comprovante excluído com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
