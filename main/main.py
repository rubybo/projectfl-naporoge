from main import app, db, bcrypt
from flask import render_template, request, redirect
from flask_login import login_user, login_required, UserMixin, LoginManager, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Length

login_manager = LoginManager()
login_manager.login_view = 'signin'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    user = db.Column(db.String(100))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))


db.create_all()


class RegisterForm(FlaskForm):
    username = StringField(label='Имя пользователя', validators=[Length(min=2, max=30)], render_kw={'class': 'form-control', 'placeholder': 'Имя пользователя'})
    password = PasswordField(label='Пароль', validators=[Length(min=2, max=18)], render_kw={'placeholder': 'Пароль', 'class': 'form-control'})
    boolean = BooleanField(label='Согласиться с политикой конфиденциальности')
    submit = SubmitField(label='Создать аккаунт', render_kw={'class': 'btn btn-primary'})


class LoginForm(FlaskForm):
    username = StringField(label='Имя пользователя', validators=[Length(min=2, max=30)], render_kw={'placeholder': 'Имя пользователя', 'class': 'form-control'})
    password = PasswordField(label='Пароль', validators=[Length(min=2, max=18)], render_kw={'placeholder': 'Пароль', 'class': 'form-control'})
    boolean = BooleanField()
    submit = SubmitField(label='Войти', render_kw={'class': 'btn btn-primary'})


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')


@app.route('/dashboard/<int:id>')
@login_required
def dashboard(id):
    username = User.query.get(id)
    return render_template('dashboard.html', username=username)


@app.route('/')
def index():
    posts = Posts.query.all()
    return render_template('index.html', posts=posts)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect('/dashboard/' + str(user.id))
    return render_template('login.html', form=form)


@app.route('/mission')
def mission():
    return render_template('mission.html')


@app.route('/about-us')
def about_us():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/courses')
def courses():
    return render_template('courses.html')


@app.route('/price')
def price():
    return render_template('price.html')


@app.route('/addpost', methods=['GET', 'POST'])
def addpost():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user = request.form['user']
        post = Posts(title=title, content=content, user=user)
        db.session.add(post)
        db.session.commit()
        return redirect('/')
    return render_template('posts.html')


@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect('/signin')
    return render_template('register.html', form=form)
