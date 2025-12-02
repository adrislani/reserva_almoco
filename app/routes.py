from flask import Blueprint, request, session, jsonify, render_template
from datetime import datetime, timedelta
from .models import db, User, Reservation

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template("index.html")

@main.route('/me')
def me():
    if 'user_id' not in session:
        return jsonify({"error": "não autenticado"}), 401

    user = User.query.get(session['user_id'])
    return jsonify({
        "id": user.id,
        "nome": user.nome,
        "nivel": user.nivel,
        "email": user.email,
        "matricula": user.matricula,
        "blockedUntil": user.blocked_until.isoformat() if user.blocked_until else None
    })

@main.route('/signup', methods=['POST'])
def signup():
    data = request.json

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email já cadastrado"}), 400

    if User.query.filter_by(matricula=data['matricula']).first():
        return jsonify({"error": "Matrícula já cadastrada"}), 400

    user = User(
        matricula=data['matricula'],
        nome=data['nome'],
        nivel=data['nivel'],
        email=data['email'],
        senha=data['senha']
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Cadastro realizado com sucesso"})


@main.route('/login', methods=['POST'])
def login():
    data = request.json

    user = User.query.filter_by(matricula=data['matricula']).first()

    if not user or user.senha != data['senha']:
        return jsonify({"error": "Credenciais inválidas"}), 401

    if user.blocked_until and user.blocked_until > datetime.utcnow():
        return jsonify({"error": "Usuário bloqueado temporariamente"}), 403

    session['user_id'] = user.id

    return jsonify({
        "id": user.id,
        "nome": user.nome,
        "nivel": user.nivel,
        "email": user.email,
        "matricula": user.matricula,
        "blockedUntil": user.blocked_until.isoformat() if user.blocked_until else None
    })


@main.route('/logout')
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logout realizado"})

@main.route('/reserve', methods=['POST'])
def reserve():
    if 'user_id' not in session:
        return jsonify({"error": "Não autenticado"}), 401

    data = request.json
    user = User.query.get(session['user_id'])

    date = datetime.utcnow().date().isoformat()
    time = datetime.utcnow().strftime("%H:%M")

    existing = Reservation.query.filter_by(
        user_id=user.id,
        date=date,
        period=data['period'],
        status='active'
    ).first()

    if existing:
        return jsonify({"error": "Você já reservou essa refeição hoje"}), 400

    qr_code = f"{user.id}-{data['period']}-{date}-{int(datetime.utcnow().timestamp())}"

    reservation = Reservation(
        user_id=user.id,
        period=data['period'],
        date=date,
        time=time,
        qr_code=qr_code
    )

    db.session.add(reservation)
    db.session.commit()

    return jsonify({
        "message": "Reserva criada",
        "qr_code": qr_code
    })

@main.route('/reservations')
def get_reservations():
    if 'user_id' not in session:
        return jsonify({"error": "Não autenticado"}), 401

    user_id = session['user_id']

    reservations = Reservation.query.filter_by(user_id=user_id).order_by(
        Reservation.created_at.desc()
    ).all()

    result = []
    for r in reservations:
        result.append({
            "id": r.id,
            "period": r.period,
            "date": r.date,
            "time": r.time,
            "status": r.status,
            "attended": r.attended,
            "qr_code": r.qr_code
        })

    return jsonify(result)

@main.route('/cancel', methods=['POST'])
def cancel():
    if 'user_id' not in session:
        return jsonify({"error": "Não autenticado"}), 401

    data = request.json
    reservation = Reservation.query.get(data['id'])

    if not reservation or reservation.user_id != session['user_id']:
        return jsonify({"error": "Reserva não encontrada"}), 404

    reservation.status = 'cancelled'
    db.session.commit()

    return jsonify({"message": "Reserva cancelada"})


@main.route('/register-attendance', methods=['POST'])
def register_attendance():
    data = request.json

    reservation = Reservation.query.filter_by(qr_code=data['qr']).first()

    if not reservation:
        return jsonify({"error": "QR inválido"}), 404

    reservation.attended = True
    db.session.commit()

    return jsonify({"message": "Presença registrada"})


@main.route('/mark-absence', methods=['POST'])
def mark_absence():
    data = request.json

    reservation = Reservation.query.get(data['id'])

    if not reservation:
        return jsonify({"error": "Reserva não encontrada"}), 404

    reservation.attended = False
    user = reservation.user

    user.blocked_until = datetime.utcnow() + timedelta(days=1)

    db.session.commit()

    return jsonify({"message": "Falta registrada e usuário bloqueado"})
