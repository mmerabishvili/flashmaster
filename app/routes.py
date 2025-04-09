from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User, Flashcard
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    return render_template('home.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('main.register'))

        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password.')
            return redirect(url_for('main.login'))

        login_user(user)
        flash('Login successful!')
        return redirect(url_for('main.home'))

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.login'))

@main.route('/flashcards/new', methods=['GET','POST'])
@login_required
def create_flashcard():
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        topic = request.form.get('topic')

        if not question or not answer:
            flash("Both question and answer are required.")
            return redirect(url_for('main.create_flashcard'))
        
        new_card = Flashcard(question = question, answer = answer, topic = topic, user_id = current_user.id)

        db.session.add(new_card)
        db.session.commit()

        flash("Flashcard created successfully!")
        return redirect(url_for('main.view_flashcards'))

    return render_template('create_flashcard.html')

@main.route('/flashcards')
@login_required
def view_flashcards():
    flashcards = Flashcard.query.filter_by(user_id=current_user.id).all()
    return render_template('view_flashcards.html', flashcards=flashcards)

@main.route('/flashcards/<int:id>/delete', methods=['POST'])
@login_required
def delete_flashcard(id):
    card = Flashcard.query.get_or_404(id)

    if card.user_id != current_user.id:
        flash("You don't have permission to delete this flashcard.")
        return redirect(url_for('main.view_flashcards'))

    db.session.delete(card)
    db.session.commit()
    flash("Flashcard deleted successfully.")
    return redirect(url_for('main.view_flashcards'))
