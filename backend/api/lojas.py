from flask import Blueprint, jsonify, request
from backend.models import Loja
from backend.extensions import db
from backend.utils.validators import validar_cnpj, validar_email

lojas_bp = Blueprint('lojas_bp', __name__, url_prefix='/api/lojas')

@lojas_bp.route('/', methods=['GET'])
def get_lojas():
    try:
        lojas = Loja.query.all()
        return jsonify([loja.to_dict() for loja in lojas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lojas_bp.route('/<int:loja_id>', methods=['GET'])
def get_loja(loja_id):
    try:
        loja = Loja.query.get_or_404(loja_id)
        return jsonify(loja.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lojas_bp.route('/', methods=['POST'])
def create_loja():
    data = request.get_json()
    if not data or not data.get('nome'):
        return jsonify({'error': 'Nome é obrigatório'}), 400

    if 'cnpj' in data and not validar_cnpj(data['cnpj']):
        return jsonify({'error': 'CNPJ inválido'}), 400

    if 'email' in data and not validar_email(data['email']):
        return jsonify({'error': 'Email inválido'}), 400

    try:
        nova_loja = Loja(
            nome=data['nome'],
            cnpj=data.get('cnpj'),
            telefone=data.get('telefone'),
            email=data.get('email'),
            endereco=data.get('endereco'),
            contato=data.get('contato'),
            cidade=data.get('cidade'),
            estado=data.get('estado')
        )
        db.session.add(nova_loja)
        db.session.commit()
        return jsonify(nova_loja.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@lojas_bp.route('/<int:loja_id>', methods=['PUT'])
def update_loja(loja_id):
    loja = Loja.query.get_or_404(loja_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    if 'cnpj' in data and not validar_cnpj(data['cnpj']):
        return jsonify({'error': 'CNPJ inválido'}), 400

    if 'email' in data and not validar_email(data['email']):
        return jsonify({'error': 'Email inválido'}), 400

    try:
        loja.nome = data.get('nome', loja.nome)
        loja.cnpj = data.get('cnpj', loja.cnpj)
        loja.telefone = data.get('telefone', loja.telefone)
        loja.email = data.get('email', loja.email)
        loja.endereco = data.get('endereco', loja.endereco)
        loja.contato = data.get('contato', loja.contato)
        loja.cidade = data.get('cidade', loja.cidade)
        loja.estado = data.get('estado', loja.estado)
        db.session.commit()
        return jsonify(loja.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@lojas_bp.route('/<int:loja_id>', methods=['DELETE'])
def delete_loja(loja_id):
    loja = Loja.query.get_or_404(loja_id)
    try:
        db.session.delete(loja)
        db.session.commit()
        return jsonify({'message': 'Loja excluída com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
