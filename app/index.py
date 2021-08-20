from flask import Flask, render_template, request, redirect, url_for, flash, session
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('mysecretkey')
app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ['MYSQL_ROOT_PASSWORD']
app.config['MYSQL_DATABASE_DB'] = 'app_db'
mysql = MySQL()
mysql.init_app(app)

app.secret_key = os.urandom(16)


@app.route('/')
def Index():
    return redirect(url_for('practica2'))

@app.route('/basededatos/')
def basedatos():
    return redirect(url_for('practica2'))

@app.route('/basededatos/practica2', methods=['POST', 'GET'])
def practica2():
    if request.method == 'POST':
        cur = mysql.get_db().cursor()
        cur.execute("SELECT password_hash FROM Users WHERE name = %s", (request.form['name']))
        data = cur.fetchone()
        cur.close()
        if data is not None:
            data = data[0]
            if check_password_hash(data, request.form['password']):
                session['name'] = request.form['name']
                return redirect(url_for('books'))
            # cur.execute("INSERT INTO Users (name, password) VALUES (%s, %s)", (request.form['name'], generate_password_hash(request.form['password'])))
            # mysql.get_db().commit()
            # flash('Usuario creado correctamente')
            return 'Mal'
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM Users')
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', users=data)


@app.route('/basededatos/practica2/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        cur = mysql.get_db().cursor()
        if request.form['status'] != 'activo' and request.form['status'] != 'inactivo':
            return render_template('signup.html')
        hashed_password = generate_password_hash(request.form['password'], method='md5')
        cur.execute("INSERT INTO Users(name, password, password_hash, status) VALUES(%s, %s, %s, %s)", (request.form['name'], request.form['password'], hashed_password, request.form['status']))
        mysql.get_db().commit()
        cur.close()
        return redirect(url_for('practica2'))
    return render_template('signup.html')

@app.route('/basededatos/practica2/books', methods=['GET', 'POST'])
def books():
    if not 'name' in session:
        return 'You are not logged in'
    if request.method == 'POST':
        cur = mysql.get_db().cursor()
        cur.execute('SELECT * FROM Books WHERE title = %s', (request.form['book_title']))
        data = cur.fetchall()
        cur.close()
        return render_template('books.html', books=data)
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM Books')
    data = cur.fetchall()
    cur.close()
    return render_template('books.html', books=data)


@app.route('/basededatos/practica2/edit/book/<string:id>', methods=['GET', 'POST'])
def edit_book(id):
    if not 'name' in session:
        return 'You are not logged in'
    if request.method == 'POST':
        book_title = request.form['book_title']
        book_price = request.form['book_price']
        cur = mysql.get_db().cursor()
        cur.execute('UPDATE Books SET title = %s, price = %s WHERE id = %s', (book_title, book_price, id))
        mysql.get_db().commit()
        cur.close()
        return redirect(url_for('books'))
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM Books WHERE id = %s', (id))
    data = cur.fetchone()
    cur.close()
    return render_template('edit_book.html', books=data)


@app.route('/basededatos/practica2/books/add', methods=['POST'])
def insert_book():
    if request.method == 'POST' and session['name'] == 'admin':
        book_title = request.form['book_title']
        book_price = request.form['book_price']
        cur = mysql.get_db().cursor()
        cur.execute("INSERT INTO Books (title, price) VALUES (%s,%s)", (book_title, book_price))
        mysql.get_db().commit()
        return redirect(url_for('books'))


@app.route('/basededatos/practica2/delete/book/<string:id>', methods = ['POST', 'GET'])
def delete_book(id):
    if session['name'] == 'admin':
        cur = mysql.get_db().cursor()
        cur.execute('DELETE FROM Books WHERE id = {0}'.format(id))
        mysql.get_db().commit()
        return redirect(url_for('books'))


@app.route('/basededatos/practica2/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('name', None)
    return redirect(url_for('practica2'))