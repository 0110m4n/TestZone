import os
import sys
import threading
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, redirect, jsonify, request
from flask_login import LoginManager
from src.models.user import db, User, Module, Quiz
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.dashboard import dashboard_bp
from src.routes.modules import modules_bp
import docker

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'testzone_secret_key_2024'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

def wait_for_port(container, port_key='8000/tcp', retries=10, delay=1):
    for _ in range(retries):
        container.reload()
        port_info = container.attrs['NetworkSettings']['Ports'].get(port_key)
        if port_info:
            return port_info[0]['HostPort']
        time.sleep(delay)
    return None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(modules_bp)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

sandbox_timeouts = {}

def init_database():
    with app.app_context():
        db.create_all()
        modules_data = [
            {'name': 'XSS', 'description': 'Cross-Site Scripting', 'total_pages': 4},
            {'name': 'LFI', 'description': 'Local File Inclusion', 'total_pages': 3},
            {'name': 'IDOR', 'description': 'Insecure Direct Object References', 'total_pages': 3},
            {'name': 'PATH_TRAVERSAL', 'description': 'Path Traversal', 'total_pages': 3}
        ]
        for module_data in modules_data:
            if not Module.query.filter_by(name=module_data['name']).first():
                module = Module(**module_data)
                db.session.add(module)
        db.session.commit()
        create_quiz_questions()

def create_quiz_questions():
    xss_module = Module.query.filter_by(name='XSS').first()
    if xss_module and not Quiz.query.filter_by(module_id=xss_module.id).first():
        xss_questions = [
            {'question': 'Que signifie XSS ?', 'option_a': 'Cross-Site Scripting', 'option_b': 'Cross-System Security', 'option_c': 'XML Site Script', 'option_d': 'eXtended Security System', 'correct_answer': 'A'},
            {'question': 'Quel type de XSS est stocké sur le serveur ?', 'option_a': 'Reflected XSS', 'option_b': 'Stored XSS', 'option_c': 'DOM-based XSS', 'option_d': 'Blind XSS', 'correct_answer': 'B'},
            {'question': 'Quelle balise HTML est couramment utilisée pour les attaques XSS ?', 'option_a': '<div>', 'option_b': '<p>', 'option_c': '<script>', 'option_d': '<img>', 'correct_answer': 'C'}
        ]
        for q in xss_questions:
            quiz = Quiz(module_id=xss_module.id, **q)
            db.session.add(quiz)
    db.session.commit()

def auto_stop_sandbox(container_name, delay_sec):
    time.sleep(delay_sec)
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        if container.status == 'running':
            container.stop()
            container.remove()
            sandbox_timeouts.pop(container_name, None)
    except Exception:
        pass

def stop_all_sandboxes(except_name=None):
    client = docker.from_env()
    names = ['sandbox-xss', 'sandbox-lfi', 'sandbox-idor', 'sandbox-path-traversal']
    for name in names:
        if name != except_name:
            try:
                container = client.containers.get(name)
                if container.status == 'running':
                    container.stop()
                    container.remove()
                sandbox_timeouts.pop(name, None)
            except Exception:
                pass

@app.route('/start_sandbox/<string:vuln>')
def start_sandbox(vuln):
    client = docker.from_env()
    container_name = f'sandbox-{vuln}'
    stop_all_sandboxes(except_name=container_name)
    try:
        container = client.containers.get(container_name)
        if container.status != 'running':
            container.start()
    except docker.errors.NotFound:
        container = client.containers.run(
            image=f'sandbox-{vuln}',
            detach=True,
            ports={'8000/tcp': None},
            name=container_name,
            auto_remove=True
        )
    host_port = wait_for_port(container, '8000/tcp', retries=20, delay=0.5)
    if host_port is None:
        return jsonify({'error': "Le port 8000/tcp n'a pas été mappé"}), 500
    url = f'http://{request.host.split(":")[0]}:{host_port}'
    if container_name not in sandbox_timeouts:
        t = threading.Thread(target=auto_stop_sandbox, args=(container_name, 3600), daemon=True)
        sandbox_timeouts[container_name] = t
        t.start()
    return jsonify({'sandbox_url': url})

@app.route('/stop_sandbox/<string:vuln>', methods=['POST'])
def stop_sandbox(vuln):
    client = docker.from_env()
    container_name = f'sandbox-{vuln}'
    try:
        container = client.containers.get(container_name)
        container.stop()
        container.remove()
        sandbox_timeouts.pop(container_name, None)
        return jsonify({"status": "sandbox removed"})
    except docker.errors.NotFound:
        return jsonify({"error": "not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return redirect('/login')

@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path and path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "Page not found", 404

@app.route('/sandbox_status/<string:vuln>')
def sandbox_status(vuln):
    import docker
    client = docker.from_env()
    container_name = f'sandbox-{vuln}'
    try:
        container = client.containers.get(container_name)
        is_running = container.status == 'running'
    except Exception:
        is_running = False
    return jsonify({"running": is_running})

if __name__ == '__main__':
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
