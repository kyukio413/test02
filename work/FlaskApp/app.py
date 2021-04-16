from flask import Flask, render_template, session, request, redirect, url_for
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename


app = Flask(__name__)

key = os.urandom(21)
app.secret_key = key

id_pwd = {'Conan': 'Heiji'}

URI = 'postgresql://postgres:postgres@localhost/flasktest'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = URI
db = SQLAlchemy(app)

class Data(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(30), index=True, unique=True)
  file_path = db.Column(db.String(64), index=True, unique=True)
  dt = db.Column(db.DateTime, nullable=False, default=datetime.now)

@app.cli.command('initdb')
def initdb():
  db.create_all()

@app.route('/')
def index():
  if not session.get('login'):
    return redirect(url_for('login'))
  else:
    data = Data.query.all()
    return render_template('index.html', data=data)

@app.route('/login')
def login():
  return render_template('login.html')

@app.route('/logincheck', methods=['POST'])
def logincheck():
  user_id = request.form['user_id']
  password = request.form['password']

  if user_id in id_pwd:
    if password == id_pwd[user_id]:
      session['login'] = True
    else:
      session['login'] = False
  else:
    session['login'] = False
  
  if session['login']:
    return redirect(url_for('index'))
  else:
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
  session.pop('login', None)
  return redirect(url_for('index'))

#ファイルアップロード
@app.route('/upload')
def upload():
  return render_template('upload.html')

@app.route('/register', methods=['POST'])
def register():
  title = request.form['title']
  f = request.files['file']
  file_path = 'static/' + secure_filename(f.filename)
  f.save(file_path)

  registered_file = Data(title=title, file_path=file_path)
  db.session.add(registered_file)
  db.session.commit()

  return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
  data = Data.query.get(id)
  delete_file = data.file_path
  db.session.delete(data)
  db.session.commit()
  os.remove(delete_file)
  return redirect(url_for('index'))


@app.route('/kaminari')
def kaminari():
  return '霹靂一閃'


if __name__ == '__main__':
  app.run(debug=True)