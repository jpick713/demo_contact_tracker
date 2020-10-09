from flask import Blueprint, url_for, request, redirect, render_template, flash
from app.models import User
from app import db
from flask import current_app as app
from .forms import LoginForm
from flask_login import current_user, login_user, login_required, logout_user

# Blueprint Configuration
auth_bp = Blueprint(
    'auth_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@auth_bp.route('/auth/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        redirect('/index')
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid Username or Password', 'danger')
            return redirect(url_for('auth_bp.login'))
        else:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = 'http://127.0.0.1:5000/index'
                return redirect(url_for('main_bp.contact_tracker'))
    return render_template('login.html',title='Sign in', form=form, user=None)


@auth_bp.route("/auth/logout", methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))