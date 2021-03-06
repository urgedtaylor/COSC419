from flask import Flask, render_template, Markup, request, flash, redirect, url_for, session
from flask_login import LoginManager, login_required, UserMixin, login_user, current_user, logout_user
from flask_wtf import FlaskForm
from flask_cors import CORS, cross_origin
from wtforms import Form, PasswordField, StringField, validators, ValidationError, BooleanField
# from passlib.hash import sha256_crypt
import random
from flask_sqlalchemy import SQLAlchemy

MyApp = Flask(__name__)
CORS(MyApp)
MyApp.config.from_pyfile('config.py')

db = SQLAlchemy(MyApp)
login_manager = LoginManager(MyApp)
login_manager.init_app(MyApp)
login_manager.login_view = 'login'

class users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100))

    def __repr__(self):
        return '<User %r>' % self.username
@MyApp.route("/")
def re():
    return redirect(url_for('template'))
@MyApp.route("/home")
def template():
    return render_template("index.html")
@MyApp.route("/gifs")
@cross_origin()
def giphs():
    return render_template("giphy.html")

@MyApp.errorhandler(403)
def forbiddenerror():
    return render_template('403_page.html'), 403


def check_user_pass(form, username, password):
    if users.query.filter_by(username=username.data).first():
        raise ValidationError('Username already exists')
def validate_user(form, username):
    if users.query.filter_by(username=username.data).first():
        raise ValidationError('Username already exists')
def validate_email(form, email):
    if users.query.filter_by(email=email.data).first():
        raise ValidationError('Email already exists')

class Register(Form):
    username = StringField(
        'UserName:', [
            validators.Required(), validate_user])
    email = StringField(
        'Email:', [
            validators.Email(
                message=('Not a valid email.')), validate_email])
    password = PasswordField(
        'Password:', [
            validators.DataRequired(), validators.EqualTo(
                'confirm', message=('Passwords must match'))])
    confirm = PasswordField('Confirm:')

class Login(Form):
    username = StringField(
        'UserName:', [
            validators.Required()])
    password = PasswordField(
        'Password:', [
            validators.DataRequired()
                ])
    remember = BooleanField('Remeber me')
@MyApp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
	return render_template('index.html')
    form = Login(request.form)
    if request.method == 'POST' and form.validate():
	user = users.query.filter_by(username=form.username.data).first()
	if user:
            login_user(user, remember=form.remember.data)
            return redirect(url_for('welcome'))
    
    if request.method == 'POST':
	flash('Login Unsuccessful.')

    return render_template('login.html',
                           form=form)

@MyApp.route("/welcome")
@login_required
def welcome():
  return render_template('welcome.html')


@MyApp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
	return render_template('index.html')
    form = Register(request.form)
    if request.method == 'POST' and form.validate():
        user = users(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@MyApp.route("/logout")
@login_required
def logout():
   logout_user()
   return redirect(url_for("login")) 


@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))


if __name__ == "__main__":
    MyApp.run()

