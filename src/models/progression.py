from src.models.user import db

class Progression(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    module_id = db.Column(db.Integer, nullable=False)
    page = db.Column(db.Integer, default=0)
    quiz_score = db.Column(db.Integer, default=0)
