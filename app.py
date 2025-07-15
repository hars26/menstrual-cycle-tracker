from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import matplotlib

matplotlib.use('Agg')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:harshini26@localhost/menstrual_tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


with app.app_context():
    db.create_all()

def calculate_hormone_levels(day, cycle_length=28):
    max_estrogen = 200
    min_estrogen = 50
    max_progesterone = 25
    min_progesterone = 1
    estrogen = min_estrogen + (max_estrogen - min_estrogen) * np.sin(np.pi * day / cycle_length)

    if day < cycle_length / 2:
        progesterone = min_progesterone
    else:
        progesterone = min_progesterone + (max_progesterone - min_progesterone) * np.sin(np.pi * (day - cycle_length / 2) / (cycle_length / 2))
    
    return estrogen, progesterone

def predict_next_period(last_period_start, cycle_length=28):
    last_period_date = datetime.strptime(last_period_start, "%Y-%m-%d")
    next_period_date = last_period_date + timedelta(days=cycle_length)
    return next_period_date

def create_hormone_plot(cycle_length=28):
    days = np.arange(1, cycle_length + 1)
    estrogen_levels = []
    progesterone_levels = []

    for day in days:
        estrogen, progesterone = calculate_hormone_levels(day, cycle_length)
        estrogen_levels.append(estrogen)
        progesterone_levels.append(progesterone)

    plt.figure(figsize=(10, 5))
    plt.plot(days, estrogen_levels, label="Estrogen Level", color="magenta")
    plt.plot(days, progesterone_levels, label="Progesterone Level", color="blue")
    plt.xlabel("Day of Cycle")
    plt.ylabel("Hormone Level")
    plt.title("Estrogen and Progesterone Levels Throughout Menstrual Cycle")
    plt.legend()
    plt.grid(True)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    return plot_data

def predict_ovulation_phase(cycle_length=28):
    ovulation_day = cycle_length // 2
    ovulation_window_start = ovulation_day - 2
    ovulation_window_end = ovulation_day + 2
    max_estrogen = 200
    min_estrogen = 50
    estrogen_levels = [
        min_estrogen + (max_estrogen - min_estrogen) * np.sin(np.pi * day / cycle_length)
        for day in range(1, cycle_length + 1)
    ]

    return {
        "ovulation_day": ovulation_day,
        "ovulation_window": (ovulation_window_start, ovulation_window_end),
        "peak_estrogen_levels": [estrogen_levels[day - 1] for day in range(ovulation_window_start, ovulation_window_end + 1)]
    }

def predict_current_phase(day, cycle_length=28):
    menstrual_phase_end = 5
    follicular_phase_end = cycle_length // 2
    ovulation_phase_start = follicular_phase_end - 2
    ovulation_phase_end = follicular_phase_end + 2

    if day <= menstrual_phase_end:
        return "Menstrual"
    elif day <= ovulation_phase_start:
        return "Follicular"
    elif day <= ovulation_phase_end:
        return "Ovulation"
    else:
        return "Luteal"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not email or not password or not confirm_password:
            flash('All fields are required for registration.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already registered. Please log in.', 'danger')
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'danger')
        return redirect(url_for('login'))

    username = session.get('username', 'User')
    estrogen = progesterone = next_period_start = None
    plot_url = None
    ovulation_info = None
    current_phase = None
    today = datetime.now()

    last_period_start = session.get('last_period_start')
    cycle_length = session.get('cycle_length')
    day = session.get('day')

    if last_period_start and cycle_length and day:
        day = int(day)
        cycle_length = int(cycle_length)

        # Validate cycle_length and day
        if not (21 <= cycle_length <= 35):
            flash('Cycle length must be between 21 and 35 days.', 'danger')
            return redirect(url_for('dashboard'))

        if not (1 <= day <= cycle_length):
            flash(f'Day must be between 1 and {cycle_length}.', 'danger')
            return redirect(url_for('dashboard'))

        estrogen, progesterone = calculate_hormone_levels(day, cycle_length)
        next_period_start = predict_next_period(last_period_start, cycle_length)
        plot_url = create_hormone_plot(cycle_length)
        ovulation_info = predict_ovulation_phase(cycle_length)
        current_phase = predict_current_phase(day, cycle_length)

    if request.method == 'POST':
        last_period_start = request.form.get('last_period_start')
        cycle_length = request.form.get('cycle_length')
        day = request.form.get('day')

        if not last_period_start or not cycle_length or not day:
            flash('All fields are required.', 'danger')
            return redirect(url_for('dashboard'))

        try:
            cycle_length = int(cycle_length)
            day = int(day)

            # Validate cycle_length and day again after form submission
            if not (21 <= cycle_length <= 35):
                flash('Cycle length must be between 21 and 35 days.', 'danger')
                return redirect(url_for('dashboard'))

            if not (1 <= day <= cycle_length):
                flash(f'Day must be between 1 and {cycle_length}.', 'danger')
                return redirect(url_for('dashboard'))

            session['last_period_start'] = last_period_start
            session['cycle_length'] = cycle_length
            session['day'] = day

            estrogen, progesterone = calculate_hormone_levels(day, cycle_length)
            next_period_start = predict_next_period(last_period_start, cycle_length)
            plot_url = create_hormone_plot(cycle_length)
            ovulation_info = predict_ovulation_phase(cycle_length)
            current_phase = predict_current_phase(day, cycle_length)

            flash('Predictions calculated successfully.', 'success')
        except ValueError:
            flash('Please enter valid numeric data.', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    return render_template('dashboard.html', username=username, estrogen=estrogen,
                           progesterone=progesterone, next_period_start=next_period_start,
                           plot_url=plot_url, today=today.date(), ovulation_info=ovulation_info,
                           current_phase=current_phase)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
