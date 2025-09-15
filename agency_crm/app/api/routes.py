from flask import jsonify, request, current_app
from werkzeug.security import check_password_hash
from functools import wraps
import secrets
import os
from app import db
from app.models import User, Brand, Company
from app.api import bp

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return jsonify({'error': 'API key required'}), 401

        expected_api_key = current_app.config.get('API_KEY')
        if not expected_api_key or api_key != expected_api_key:
            return jsonify({'error': 'Invalid API key'}), 401

        return f(*args, **kwargs)
    return decorated_function

@bp.route('/authenticate', methods=['POST'])
@require_api_key
def authenticate():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    user_data = {
        'id': user.id,
        'email': user.email,
        'name': f"{user.first_name} {user.last_name}",
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'is_active': True
    }

    return jsonify({'success': True, 'user': user_data}), 200

@bp.route('/users/<int:user_id>', methods=['GET'])
@require_api_key
def get_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_data = {
        'id': user.id,
        'email': user.email,
        'name': f"{user.first_name} {user.last_name}",
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'is_active': True
    }

    return jsonify({'user': user_data}), 200

@bp.route('/users', methods=['GET'])
@require_api_key
def get_all_users():
    users = User.query.all()

    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'email': user.email,
            'name': f"{user.first_name} {user.last_name}",
        'first_name': user.first_name,
        'last_name': user.last_name,
            'role': user.role,
            'is_active': True
        })

    return jsonify({'users': users_data}), 200

@bp.route('/brands', methods=['GET'])
@require_api_key
def get_brands():
    """Get all active brands with company information"""
    try:
        brands = Brand.query.filter_by(status='active').join(Company).all()

        brands_data = []
        for brand in brands:
            brands_data.append({
                'id': brand.id,
                'name': brand.name,
                'company_id': brand.company_id,
                'company_name': brand.company.name,
                'full_name': f"{brand.company.name} - {brand.name}",
                'status': brand.status,
                'created_at': brand.created_at.isoformat()
            })

        return jsonify({'brands': brands_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/brands/<int:brand_id>', methods=['GET'])
@require_api_key
def get_brand(brand_id):
    """Get specific brand by ID"""
    try:
        brand = Brand.query.filter_by(id=brand_id, status='active').join(Company).first()

        if not brand:
            return jsonify({'error': 'Brand not found'}), 404

        brand_data = {
            'id': brand.id,
            'name': brand.name,
            'company_id': brand.company_id,
            'company_name': brand.company.name,
            'full_name': f"{brand.company.name} - {brand.name}",
            'status': brand.status,
            'created_at': brand.created_at.isoformat()
        }

        return jsonify({'brand': brand_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/companies', methods=['GET'])
@require_api_key
def get_companies():
    """Get all active companies"""
    try:
        companies = Company.query.filter_by(status='active').all()

        companies_data = []
        for company in companies:
            companies_data.append({
                'id': company.id,
                'name': company.name,
                'vat_code': company.vat_code,
                'status': company.status,
                'created_at': company.created_at.isoformat(),
                'brand_count': len([b for b in company.brands if b.status == 'active'])
            })

        return jsonify({'companies': companies_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/user-created', methods=['POST'])
def user_created_webhook():
    from app.api.sync import sync_user_to_projects_crm

    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({'error': 'User ID required'}), 400

    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    success = sync_user_to_projects_crm(user)

    if success:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Failed to sync user'}), 500