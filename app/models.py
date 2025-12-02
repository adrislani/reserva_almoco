from datetime import datetime
from . import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(120), nullable=False)
    nivel = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    blocked_until = db.Column(db.DateTime, nullable=True)

    reservations = db.relationship('Reservation', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.matricula} - {self.nome}>"


class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    period = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(20), nullable=False)

    status = db.Column(db.String(20), default='active')

    attended = db.Column(db.Boolean, nullable=True)
    qr_code = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"<Reservation user={self.user_id} period={self.period} "
            f"date={self.date}>"
        )