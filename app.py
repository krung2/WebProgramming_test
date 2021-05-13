import pymysql
import os
import requests, json
from flask import *
from flaskext.mysql import MySQL

app = Flask(__name__)
os.environ['APP_SETTING'] = 'settings.cfg'
app.config.from_envvar('APP_SETTING')

mysql = MySQL(
    cursorclass=pymysql.cursors.DictCursor
)

mysql.init_app(app)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/logged')
def main_login():
    name = session.get('name', None)

    if name is None:
        return redirect('/')

    return render_template('index_logged.html', name=name)


@app.route('/logout')
def logout():
    del session['name']

    return redirect('/')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def api_login():
    id = request.values.get('id')
    pw = request.values.get('pw')

    conn = mysql.get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM user WHERE id = %s AND pw = %s', [id, pw])
    user = cursor.fetchone()

    if user is None:
        abort(401, "id 또는 pw를 확인해주세요")

    session['name'] = user['name']

    return redirect('/logged')


@app.route('/register')
def register():
    return render_template('join.html')


@app.route('/register', methods=['POST'])
def api_register():
    id = request.values.get('id')
    pw = request.values.get('pw')
    name = request.values.get('name')

    conn = mysql.get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM user WHERE id = %s', [id])
    user = cursor.fetchone()

    if user is not None:
        abort(401, "이미 있는 id입니다")
    else:
        cursor.execute('INSERT INTO user(id, pw, name) VALUES (%s, %s, %s)', [id, pw, name])
        conn.commit()

        return redirect('/login')

@app.route('/guestBook')
def geustBook():
    name = session.get('name', None);
    isLogin = 0

    if name is not None :
        isLogin = 1

    conn = mysql.get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM POST ORDER BY idx DESC')
    posts = cursor.fetchall()

    return render_template('guestBook.html', isLogin=isLogin, name=name, posts=posts)

@app.route('/guestBook', methods=['POST'])
def registerGuestBook():

    name = request.values.get('name')
    content = request.values.get('content')

    conn = mysql.get_db()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO post(author, content) VALUES (%s, %s)', [name, content])
    conn.commit()

    return redirect('/guestBook')

app.run(host='0.0.0.0', port=5000, debug=True)
