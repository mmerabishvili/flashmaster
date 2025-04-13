from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from . import db
from .models import User, Flashcard, Topic
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

@main.route('/topics')
@login_required
def view_topics():
    topics = Topic.query.filter_by(user_id=current_user.id).all()
    return render_template('view_topics.html', topics=topics)

@main.route('/topics/new', methods=['GET','POST'])
@login_required
def create_topic():
    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            flash("Topic name is required.")
            return redirect(url_for('main.create_topic'))
        
        new_topic = Topic(name=name, user_id=current_user.id)
        db.session.add(new_topic)
        db.session.commit()

        flash("Topic created successfully!")
        return redirect(url_for('main.create_flashcard'))

    return render_template('create_topic.html')

@main.route('/flashcards/new', methods=['GET', 'POST'])
@login_required
def create_flashcard():
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        topic_name = request.form.get('topic').strip()  

        if not question or not answer or not topic_name:
            flash("All fields are required.")
            return redirect(url_for('main.create_flashcard'))

        topic = Topic.query.filter_by(name=topic_name, user_id=current_user.id).first()
        if not topic:
            topic = Topic(name=topic_name, user_id=current_user.id)
            db.session.add(topic)
            db.session.commit()

        new_card = Flashcard(
            question=question,
            answer=answer,
            topic_id=topic.id,
            user_id=current_user.id
        )

        db.session.add(new_card)
        db.session.commit()

        flash("Flashcard created successfully!")
        return redirect(url_for('main.view_flashcards'))

    pre_filled_topic = request.args.get('topic', '')
    return render_template('create_flashcard.html', pre_filled_topic=pre_filled_topic)


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

@main.route('/flashcards/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_flashcard(id):
    card = Flashcard.query.get_or_404(id)

    if card.user_id != current_user.id:
        flash("You don't have permission to edit this flashcard.")
        return redirect(url_for('main.view_flashcards'))

    if request.method == 'POST':
        card.question = request.form.get('question')
        card.answer = request.form.get('answer')
        card.topic = request.form.get('topic')
        
        db.session.commit()
        flash("Flashcard updated successfully!")
        return redirect(url_for('main.view_flashcards'))

    return render_template('edit_flashcard.html', card=card)

@main.route('/study', methods = ['GET', 'POST'])
@login_required
def study():
    topics = Topic.query.filter_by(user_id = current_user.id).all()

    if request.method == 'POST':
        selected_topic = request.form.get('topic')
        flashcards = Flashcard.query.filter_by(user_id = current_user.id, topic_id = selected_topic).all()

        if not flashcards:
            flash("No flashcards in this topic yet.")
            return redirect(url_for('main.study'))

        session['study_flashcards'] = [f.id for f in flashcards]
        session['study_index'] = 0
        return redirect(url_for('main.study_session'))

    return render_template('study_start.html', topics=topics)

@main.route('/study/session', methods = ['GET', 'POST'])
@login_required
def study_session():
    flashcard_ids = session.get('study_flashcards', [])
    index = session.get('study_index', 0)
        
    if not flashcard_ids or index >= len(flashcard_ids):
        flash("Study session complete!")
        return redirect(url_for('main.study'))
            
    card_id = flashcard_ids[index]
    card = Flashcard.query.get_or_404(card_id)
        
    if request.method == 'POST':
        session['study_index'] += 1
        return redirect(url_for('main.study_session'))
        
    return render_template('study_session.html', card=card)