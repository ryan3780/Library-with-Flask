from flask import Flask, render_template, session, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.secret_key = 'sample_secret_key'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost:3306/books_db" 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)
migrate.init_app(app, db)

# from . import models 하면 에러나는 이유는?
from models import *

@app.route("/")
def hello():
	
	if 'log_in' in session:
		books_info = Books.query.all()
		return render_template('main.html', books_info = books_info)
	else:
		return render_template('login.html')

@app.route("/login", methods=['POST'])
def login():

	if 'log_in' in session:
		return hello()

	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		data = Users.query.filter_by(username =username, password =password).first()
		
		if data is not None :
			session['log_in'] = True
			session['username'] = username
			books_info = Books.query.all()
			db.session.close()
			# redirect -> '/' url history 찾아보기(출력 해보기)
			return redirect(url_for('hello'))
			
		return '''<script>alert('nonono'); location.href= '/';</script>'''

@app.route("/logout")
def logout():
	session.pop('log_in', None)
	return redirect(url_for('hello'))

@app.route("/register", methods=['GET','POST'])
def register():

	if request.method =='POST':
		username = request.form['username']
		email = request.form['email']
		password = request.form['password']
		check = request.form['check']
		query = Users(username, email, password)

		if password == check and len(username) != 0 and len(email) != 0 and len(password) != 0:	
			db.session.add(query)
			db.session.commit()
			db.session.close()
			return render_template('login.html')

	return 	render_template('register.html')

@app.route("/book-info/<int:bookId>")
def info(bookId):
	books_info = Books.query.filter(Books.id == bookId).all()
	print(books_info)
	return render_template('base.html', books_info=books_info)

if __name__ == "__main__":

	app.run(debug=True)