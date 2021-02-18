from flask import Flask, render_template, redirect, session, flash
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "abc123"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///feedback_app"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

connect_db(app)

# ************************* Auth Routes *************************

@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Render registration form"""

    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        flash('Account created!')
        return redirect(f'/users/{new_user.username}')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Render login form"""

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['user_id'] = user.id
            return redirect(f'/users/{user.username}')
        else:
            return redirect('/register')
    
    return render_template('login.html', form=form)


@app.route('/users/<username>')
def render_secret(username):
    """Show user secret template."""
    if "user_id" not in session:
        flash("please login first.")
        return redirect('/login')

    user = User.query.filter_by(username=username).first()
    user_feedback = Feedback.query.filter_by(username=username)

    return render_template('user.html', user=user, user_feedback=user_feedback)


@app.route('/logout')
def logout_user():
    session.pop('user_id')
    return redirect('/')


# ************************* Feedback Routes *************************
@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def render_feedback_form(username):
    form = FeedbackForm()
    user = User.query.filter_by(username=username)
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()
        return redirect(f'/users/{username}')
    
    return render_template('feedback.html', form=form)


@app.route('/feedback/<int:id>/delete', methods=["POST"])
def delete_feedback(id):
    """Delete feedback."""
    if 'user_id' not in session:
        return redirect('/login')

    feedback = Feedback.query.get_or_404(id)
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f"/users/feedback.username")


@app.route('/feedback/<int:id>/update', methods=["GET", "POST"])
def edit_feedback(id):
    """Edit feedback."""
    feedback = Feedback.query.get_or_404(id)
    if 'user_id' not in session:
        return redirect('/login')

    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()

        return redirect(f"/users/feedback.username")
    return render_template("edit.html", form=form, feedback=feedback)

