from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from src.models.user import Module, Quiz, QuizResult
from src.models.progression import Progression

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard/index.html')

@dashboard_bp.route('/sandbox')
@login_required
def sandbox():
    return render_template('dashboard/sandbox.html')

@dashboard_bp.route('/api/progress')
@login_required
def get_user_progress():
    modules = Module.query.all()
    progress_data = []
    for module in modules:
        progression = Progression.query.filter_by(user_id=current_user.id, module_id=module.id).first()
        quizzes = Quiz.query.filter_by(module_id=module.id).all()
        quiz_results = [
            QuizResult.query.filter_by(user_id=current_user.id, quiz_id=quiz.id).order_by(QuizResult.id.desc()).first()
            for quiz in quizzes
        ]
        correct_answers = sum(1 for qr in quiz_results if qr and qr.is_correct)
        total_questions = len(quizzes)
        quiz_score = (correct_answers / total_questions) * 100 if total_questions else 0
        current_page = progression.page if progression else 0
        completed = current_page >= module.total_pages
        progress_data.append({
            "module_name": module.name,
            "module_id": module.id,
            "current_page": current_page,
            "total_pages": module.total_pages,
            "completed": completed,
            "quiz_score": quiz_score if total_questions > 0 else None,
        })
    return jsonify(progress_data)
