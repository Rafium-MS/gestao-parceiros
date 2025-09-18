from flask import Blueprint, jsonify
from backend.models import Parceiro

parceiros_bp = Blueprint('parceiros_bp', __name__, url_prefix='/api/parceiros')

from flask import request
from backend.extensions import db
from backend.utils.validators import validar_cpf, validar_email

@parceiros_bp.route('/', methods=['GET'])
def get_parceiros():
    """
    Retorna uma lista de todos os parceiros.
    """
    try:
        parceiros = Parceiro.query.all()
        return jsonify([parceiro.to_dict() for parceiro in parceiros]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parceiros_bp.route('/<int:parceiro_id>', methods=['GET'])
def get_parceiro(parceiro_id):
    """
    Retorna os dados de um parceiro específico.
    """
    try:
        parceiro = Parceiro.query.get_or_404(parceiro_id)
        return jsonify(parceiro.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parceiros_bp.route('/', methods=['POST'])
def create_parceiro():
    """
    Cria um novo parceiro.
    """
    data = request.get_json()
    if not data or not data.get('nome'):
        return jsonify({'error': 'Nome é obrigatório'}), 400

    if 'cpf' in data and not validar_cpf(data['cpf']):
        return jsonify({'error': 'CPF inválido'}), 400

    if 'email' in data and not validar_email(data['email']):
        return jsonify({'error': 'Email inválido'}), 400

    try:
        novo_parceiro = Parceiro(
            nome=data['nome'],
            cpf=data.get('cpf'),
            telefone=data.get('telefone'),
            email=data.get('email'),
            endereco=data.get('endereco'),
            cidade=data.get('cidade'),
            estado=data.get('estado'),
            banco=data.get('banco'),
            agencia=data.get('agencia'),
            conta=data.get('conta'),
            tipo=data.get('tipo'),
            produto=data.get('produto'),
            valor_unidade=data.get('valor_unidade')
        )
        db.session.add(novo_parceiro)
        db.session.commit()
        return jsonify(novo_parceiro.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@parceiros_bp.route('/<int:parceiro_id>', methods=['PUT'])
def update_parceiro(parceiro_id):
    """
    Atualiza um parceiro existente.
    """
    parceiro = Parceiro.query.get_or_404(parceiro_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    if 'cpf' in data and not validar_cpf(data['cpf']):
        return jsonify({'error': 'CPF inválido'}), 400

    if 'email' in data and not validar_email(data['email']):
        return jsonify({'error': 'Email inválido'}), 400

    try:
        parceiro.nome = data.get('nome', parceiro.nome)
        parceiro.cpf = data.get('cpf', parceiro.cpf)
        parceiro.telefone = data.get('telefone', parceiro.telefone)
        parceiro.email = data.get('email', parceiro.email)
        parceiro.endereco = data.get('endereco', parceiro.endereco)
        parceiro.cidade = data.get('cidade', parceiro.cidade)
        parceiro.estado = data.get('estado', parceiro.estado)
        parceiro.banco = data.get('banco', parceiro.banco)
        parceiro.agencia = data.get('agencia', parceiro.agencia)
        parceiro.conta = data.get('conta', parceiro.conta)
        parceiro.tipo = data.get('tipo', parceiro.tipo)
        parceiro.produto = data.get('produto', parceiro.produto)
        parceiro.valor_unidade = data.get('valor_unidade', parceiro.valor_unidade)

        db.session.commit()
        return jsonify(parceiro.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@parceiros_bp.route('/<int:parceiro_id>', methods=['DELETE'])
def delete_parceiro(parceiro_id):
    """
    Exclui um parceiro.
    """
    parceiro = Parceiro.query.get_or_404(parceiro_id)
    try:
        db.session.delete(parceiro)
        db.session.commit()
        return jsonify({'message': 'Parceiro excluído com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
