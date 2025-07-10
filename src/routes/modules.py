from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from src.models.user import db, Module, Quiz, QuizResult
from src.models.progression import Progression

modules_bp = Blueprint('modules', __name__)

@modules_bp.route('/module/<module_name>')
@login_required
def module_home(module_name):
    module = Module.query.filter_by(name=module_name.upper()).first_or_404()
    return render_template(f'modules/{module_name.lower()}/index.html', module=module)

@modules_bp.route('/module/<module_name>/page/<int:page_num>')
@login_required
def module_page(module_name, page_num):
    module = Module.query.filter_by(name=module_name.upper()).first_or_404()
    progress = Progression.query.filter_by(
        user_id=current_user.id,
        module_id=module.id
    ).first()
    if not progress:
        progress = Progression(
            user_id=current_user.id,
            module_id=module.id,
            page=page_num,
            quiz_score=0
        )
        db.session.add(progress)
    else:
        if page_num > progress.page:
            progress.page = page_num
    db.session.commit()
    return render_template(f'modules/{module_name.lower()}/page{page_num}.html',
                         module=module, page_num=page_num)

@modules_bp.route('/module/<module_name>/quiz')
@login_required
def module_quiz(module_name):
    module = Module.query.filter_by(name=module_name.upper()).first_or_404()
    quizzes = Quiz.query.filter_by(module_id=module.id).all()
    return render_template('quiz/quiz.html', module=module, quizzes=quizzes)

@modules_bp.route('/api/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz_answer(quiz_id):
    data = request.get_json()
    selected_answer = data.get('answer')
    quiz = Quiz.query.get_or_404(quiz_id)
    is_correct = selected_answer == quiz.correct_answer
    quiz_result = QuizResult(
        user_id=current_user.id,
        quiz_id=quiz_id,
        selected_answer=selected_answer,
        is_correct=is_correct
    )
    db.session.add(quiz_result)
    db.session.commit()

    module = Module.query.get(quiz.module_id)
    progress = Progression.query.filter_by(
        user_id=current_user.id,
        module_id=module.id
    ).first()
    score = 0
    quizzes = Quiz.query.filter_by(module_id=module.id).all()
    for q in quizzes:
        qr = QuizResult.query.filter_by(user_id=current_user.id, quiz_id=q.id).order_by(QuizResult.id.desc()).first()
        if qr and qr.is_correct:
            score += 1
    if not progress:
        progress = Progression(
            user_id=current_user.id,
            module_id=module.id,
            page=progress.page if progress else 0,
            quiz_score=score
        )
        db.session.add(progress)
    else:
        if score > progress.quiz_score:
            progress.quiz_score = score
    db.session.commit()

    return jsonify({
        'correct': is_correct,
        'correct_answer': quiz.correct_answer
    })

@modules_bp.route('/api/quiz/<module_name>/results')
@login_required
def get_quiz_results(module_name):
    module = Module.query.filter_by(name=module_name.upper()).first_or_404()
    quizzes = Quiz.query.filter_by(module_id=module.id).all()
    correct_answers = 0
    total_questions = len(quizzes)
    for q in quizzes:
        qr = QuizResult.query.filter_by(user_id=current_user.id, quiz_id=q.id).order_by(QuizResult.id.desc()).first()
        if qr and qr.is_correct:
            correct_answers += 1
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    return jsonify({
        'score': score,
        'correct': correct_answers,
        'total': total_questions
    })
