from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from . import db
from .models import User, Flashcard, Topic, StudySession
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
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Try logging in or use another email.", 'error')
            return redirect(url_for('main.register'))

        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose another one.", 'error')
            return redirect(url_for('main.register'))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", 'error')
            return redirect(url_for('main.register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'auth')
        return redirect(url_for('main.login'))

    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')

        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid login details.', 'auth')
            return redirect(url_for('main.login'))

        login_user(user)
        flash('Login successful!', 'auth')
        return redirect(url_for('main.home'))

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'auth')
    return redirect(url_for('main.login'))

@main.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current = request.form.get('current_password')
        new = request.form.get('new_password')
        confirm = request.form.get('confirm_password')

        if not current_user.check_password(current):
            flash("Current password is incorrect.", "error")
        elif new != confirm:
            flash("New passwords do not match.", "error")
        elif len(new) < 6:
            flash("Password must be at least 6 characters.", "error")
        elif current_user.check_password(new):
            flash("New password must be different from your current password.", "error")
        else:
            current_user.set_password(new)
            db.session.commit()
            flash("Password updated successfully!", "auth")
            return redirect(url_for('main.profile'))

    return render_template('change_password.html')

@main.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    flash("Your account has been deleted.", "info")
    return redirect(url_for('main.login'))

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

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

        if name:
            new_topic = Topic(name=name, user_id=current_user.id)
            db.session.add(new_topic)
            db.session.commit()
            flash("Topic created successfully!", 'topic')
            return redirect(url_for('main.view_topics'))  
        else:
            flash("Please enter a topic name.", 'error')

    return render_template('create_topic.html')

@main.route('/topics/delete/<int:topic_id>', methods=['POST'])
@login_required
def delete_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)

    if topic.user_id != current_user.id:
        flash("You can't delete this topic.", 'error')
        return redirect(url_for('main.view_topics'))

    for card in topic.flashcards:
        db.session.delete(card)

    db.session.delete(topic)
    db.session.commit()
    flash("Topic deleted successfully.", 'topic')
    return redirect(url_for('main.view_topics'))

@main.route('/flashcards/new', methods=['GET', 'POST'])
@login_required
def create_flashcard():
    topic_name = request.args.get('topic')  

    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        topic_name = request.form.get('topic')

        if not question or not answer or not topic_name:
            flash("All fields are required.", 'flashcard')
            return redirect(url_for('main.create_flashcard'))

        topic = Topic.query.filter_by(name=topic_name, user_id=current_user.id).first()
        if not topic:
            flash("Topic not found.", 'topic')
            return redirect(url_for('main.view_topics'))

        new_card = Flashcard(
            question=question,
            answer=answer,
            topic_id=topic.id,
            user_id=current_user.id
        )
        db.session.add(new_card)
        db.session.commit()

        flash("Flashcard created successfully!", 'flashcard')
        return redirect(url_for('main.view_flashcards', topic_id=topic.id))

    return render_template('create_flashcard.html', topic=topic_name)



@main.route('/flashcards')
@login_required
def view_flashcards():
    topic_id = request.args.get('topic_id')

    if topic_id:
        topic = Topic.query.get_or_404(topic_id)
        flashcards = Flashcard.query.filter_by(user_id=current_user.id, topic_id=topic_id).all()
    else:
        topic = None
        flashcards = Flashcard.query.filter_by(user_id=current_user.id).all()

    return render_template('view_flashcards.html', flashcards=flashcards, topic=topic)


@main.route('/flashcards/<int:id>/delete', methods=['POST'])
@login_required
def delete_flashcard(id):
    card = Flashcard.query.get_or_404(id)

    if card.user_id != current_user.id:
        flash("You don't have permission to delete this flashcard.", 'error')
        return redirect(url_for('main.view_flashcards', topic_id=card.topic_id))

    db.session.delete(card)
    db.session.commit()
    flash("Flashcard deleted successfully!", 'flashcard')
    return redirect(url_for('main.view_flashcards', topic_id=card.topic_id))


@main.route('/flashcards/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_flashcard(id):
    card = Flashcard.query.get_or_404(id)

    if card.user_id != current_user.id:
        flash("You don't have permission to edit this flashcard.", 'error')
        return redirect(url_for('main.view_flashcards', topic_id = card.topic_id))

    if request.method == 'POST':
        card.question = request.form.get('question')
        card.answer = request.form.get('answer')
        db.session.commit()
        flash("Flashcard updated successfully!", 'flashcard')
        return redirect(url_for('main.view_flashcards', topic_id=card.topic_id)) 

    return render_template('edit_flashcard.html', card=card)

@main.route('/study', methods = ['GET', 'POST'])
@login_required
def study():
    topics = Topic.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        selected_topic = request.form.get('topic')
        selected_mode = request.form.get('mode')
        session['study_mode'] = selected_mode
        session.modified = True
        
        flashcards = Flashcard.query.filter_by(user_id=current_user.id, topic_id=selected_topic).all()

        if not flashcards:
            flash("No flashcards in this topic yet.", 'study')
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
    mode = session.get('study_mode', 'practice').strip().lower()
        
    if not flashcard_ids or index >= len(flashcard_ids):
        return redirect(url_for('main.study_results'))
            
    card_id = flashcard_ids[index]
    card = Flashcard.query.get_or_404(card_id)
    
    # Initialize tracking stats if needed
    if 'study_stats' not in session:
        session['study_stats'] = {}

    if request.method == 'POST':
        if mode == 'track':
            result = request.form.get('answer')
            session['study_stats'][str(card.id)] = result
            session.modified = True  # makes sure session gets updated

        session['study_index'] += 1
        return redirect(url_for('main.study_session'))

    return render_template('study_session.html',card=card,mode=mode)

@main.route('/progress')
@login_required
def progress():
    sessions = StudySession.query.filter_by(user_id=current_user.id).order_by(StudySession.timestamp.desc()).all()

    # Group sessions by topic
    from collections import defaultdict
    topics = defaultdict(list)
    for session in sessions:
        topics[session.topic.name].append(session)

    return render_template('progress.html', topics=topics)

@main.route('/study/results')
@login_required
def study_results():
    stats = session.get('study_stats', {})
    flashcard_ids = session.get('study_flashcards', [])
    topic_id = None
    correct = 0
    total = len(flashcard_ids)

    for card_id in flashcard_ids:
        if stats.get(str(card_id)) == 'correct':
            correct += 1

        # Get the topic ID from the first card (they're all from the same topic)
        if topic_id is None:
            card = Flashcard.query.get(int(card_id))
            topic_id = card.topic_id

    mode = session.get('study_mode', 'practice')

    #set a defalt value for previous in case it's a practice mode
    previous = None
    
    # Save the session only if tracking is enabled
    if mode == 'track':
        new_session = StudySession(
            user_id=current_user.id,
            topic_id=topic_id,
            correct=correct,
            total=total
        )
        db.session.add(new_session)
        db.session.commit()

        # Get the previous attempt for comparison
        previous = (
            StudySession.query
            .filter(StudySession.user_id == current_user.id, StudySession.topic_id == topic_id)
            .order_by(StudySession.timestamp.desc())
            .offset(1)
            .first()
        )

    # Clear study session data
    session.pop('study_flashcards', None)
    session.pop('study_index', None)
    session.pop('study_stats', None)
    session.pop('study_mode', None)

    return render_template('study_results.html', correct=correct, total=total, previous=previous,mode=mode)

@main.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash("Access denied. Admins only.", "error")
        return redirect(url_for('main.home'))

    users = User.query.all()
    return render_template('admin.html', users=users)

@main.route('/admin/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("Access denied.", 'error')
        return redirect(url_for('main.home'))

    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("Cannot delete an admin.", 'error')
    else:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted.", 'admin')
    
    return redirect(url_for('main.admin_panel'))

@main.route('/admin/reset/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    if not current_user.is_admin:
        flash("Access denied.", 'error')
        return redirect(url_for('main.home'))

    user = User.query.get_or_404(user_id)
    user.set_password("newpassword123")
    db.session.commit()
    flash("Password reset to 'newpassword123'.", 'admin')
    return redirect(url_for('main.admin_panel'))
