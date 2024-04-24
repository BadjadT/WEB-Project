from flask import Flask, render_template, url_for, request, flash
from flask import session, redirect, abort, g, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from forms import LoginF, RegisterF

import sqlite3
import os
from db_session import dbsession

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oaz3jgu5ug1iil9lkfsg12'

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Войдите для полного функционала сайта'
login_manager.login_message_category = 'success'

MAX_CONTENT_LENGTH = 1024 * 1024
DATABASE = "/tmd/USERS.db"
DEBUG = True
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'USERS.db')))

menu = [{'name': "Главная", 'url': '/'},
        {'name': "Профиль", 'url': 'profile'}]
lmenu = [{'name': "Вход", 'url': 'login'},
         {'name': "Регистрация", 'url': 'register'}]


@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    db.cursor().executescript('CREATE TABLE IF NOT EXISTS users ('
                              'id integer PRIMARY KEY AUTOINCREMENT,'
                              'name text NOT NULL,'
                              'email text NOT NULL,'
                              'password text NOT NULL,'
                              'avatar BLOB DEFAULT NULL);')
    db.cursor().executescript('CREATE TABLE IF NOT EXISTS posts ('
                              'id integer PRIMARY KEY AUTOINCREMENT,'
                              'user_id integer NOT NULL,'
                              'username text NOT NULL,'
                              'content text NOT NULL,'
                              'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
                              'FOREIGN KEY (user_id) REFERENCES users (id));')
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = dbsession(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/')
def index():
    posts = dbase.get_posts()

    return render_template('main.html', lmenu=lmenu, menu=menu, posts=posts, title='News')


@app.route('/create-post', methods=['POST'])
@login_required
def create_post():
    if request.method == 'POST':
        content = request.form['content']
        id = dbase.getUserByEmail(current_user.getMail())
        dbase.add_post(current_user.get_id(), id['name'], content)

    return redirect(url_for('index'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginF()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['password'], form.password.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))

        flash('Логин или пароль введены неверно', 'error')

    return render_template("login_form.html", lmenu=lmenu, menu=menu, title="Вход", form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = RegisterF()
    if form.validate_on_submit():
        hash = generate_password_hash(request.form['password'])
        res = dbase.add_user(form.name.data, form.email.data, hash)
        if res:
            user = dbase.getUserByEmail(form.email.data)
            flash("Вы успешно зарегистрированы", "success")
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(url_for('login'))
        else:
            flash("Ошибка при добавлении в БД", "error")

    return render_template("reg_form.html", lmenu=lmenu, menu=menu, title="Регистрация", form=form)


@app.route('/profile')
@login_required
def profile():
    posts = dbase.get_posts(current_user.get_id())
    User_id = current_user.get_id()
    return render_template('profile.html', lmenu=lmenu, menu=menu,
                           title=f'Профиль ', posts=posts, user_id=User_id)


@app.route('/delete_profile')
@login_required
def delete_profile():
    user_id = current_user.get_id()
    dbase.delete_profile(user_id)
    return redirect(url_for('logout'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Выход из аккаунта', 'success')
    return redirect(url_for('login'))


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ''
    a = make_response(img)
    a.headers['Content-Type'] = 'image/png'
    return a


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка загрузки", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Файл не найден", "error")
        else:
            flash("Слижком большой файл", "error")

    return redirect(url_for('profile'))


@app.route('/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def delete(id):
    if request.method == 'GET':
        dbase.delete_post(id)
    return redirect(url_for('profile'))


# ФУНКЦИЯ НЕ ГОТОВА
@app.route('/profile/user_id')
@login_required
def someones_profile(user_id):
    user = dbase.getUser(user_id)
    posts = dbase.get_posts(current_user.get_id())
    return render_template('someones_profile.html', lmenu=lmenu, menu=menu,
                           title=f'Профиль', posts=posts, user=user)


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('404.html', lmenu=lmenu, menu=menu, title='Страница не найдена')


if __name__ == "__main__":
    app.run(debug=True)
