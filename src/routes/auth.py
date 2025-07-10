from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from src.models.user import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            if request.is_json:
                return jsonify({'success': True, 'redirect': '/dashboard'})
            else:
                return redirect('/dashboard')
        else:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Nom d\'utilisateur ou mot de passe incorrect'})
            else:
                flash('Nom d\'utilisateur ou mot de passe incorrect')
                return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
        else:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
        
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return jsonify({'success': False, 'message': 'Ce nom d\'utilisateur existe déjà'})
            else:
                flash('Ce nom d\'utilisateur existe déjà')
                return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'success': False, 'message': 'Cette adresse email existe déjà'})
            else:
                flash('Cette adresse email existe déjà')
                return render_template('auth/register.html')
        
        # Créer le nouvel utilisateur
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        
        if request.is_json:
            return jsonify({'success': True, 'redirect': '/dashboard'})
        else:
            return redirect('/dashboard')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@auth_bp.route('/api/user')
@login_required
def get_current_user():
    return jsonify(current_user.to_dict())

