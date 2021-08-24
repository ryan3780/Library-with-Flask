from flask import Flask, render_template, session, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import date, timedelta
from flask_wtf.csrf import CSRFProtect #csrf
from form import RegisterForm
import re

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
	form = RegisterForm()
	if 'log_in' in session:
		books_info = Book.query.all()
		return render_template('main.html', books_info = books_info)
	else:
		return render_template('login.html', form= form)

@app.route("/login", methods=['POST'])
def login():
	form = RegisterForm()

	if 'log_in' in session:
		return redirect(url_for('main.html', form = form))

	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		data = User.query.filter_by(email = email, password =password).first()
		
		if data is not None :
			session['log_in'] = True
			session['username'] = email
			db.session.close()
			# redirect -> '/' url history 찾아보기(출력 해보기)
			return redirect(url_for('hello', form= form))

		flash('이메일과 비밀번호를 다시 입력해주세요.')	
		return redirect(url_for('hello', form= form))

@app.route("/logout")
def logout():
	session.pop('log_in', None)
	return redirect(url_for('hello'))


@app.route("/register", methods=['GET','POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		username = form.data.get('username')
		email = form.data.get('email')
		password = form.data.get('password')

		query = User(username, email, password)

		username_validation = re.compile('^[가-힣a-zA-Z]+$')
		email_validatioin = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
		# 최소 8자, 하나 이상의 문자, 하나의 숫자 및 하나의 특수 문자
		pw_validation = re.compile('^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$')
		# 최소 8 자, 하나 이상의 문자, 하나의 숫자, 하나의 특수 문자
		# pw_validation = re.compile('^(?=.*[a-zA-Z])(?=.*[0-9])(?=.*[^\w\s]).*{8,}$ | ^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{10,}$')
		# print(bool(username_validation.match(username)), bool(email_validatioin.match(email)), bool(pw_validation.match(password)))
		
		if bool(username_validation.match(username)) and bool(email_validatioin.match(email)) and bool(pw_validation.match(password)):
			db.session.add(query)
			db.session.commit()
			db.session.close()
			flash('가입을 정상적으로 완료했습니다.')
			return render_template('login.html', form = form)
	
	return 	render_template('register.html', form = form)

@app.route("/book-info/<int:bookId>")
def info(bookId):
	books_info = Book.query.filter(Book.id == bookId).all()
	return render_template('book_info.html', books_info=books_info)


@app.route("/rent-book/<int:bookId>") 
# ajax or main_page와 같은 주소로 처리 or 자바스크립트로 스크롤 위치 값 local storage로 저장해놨다가 불러와서 적용하기, '#' url 주소 뒤에 붙이는 방법 id 사용
def rent(bookId):
	customer= User.query.filter_by(email = session['username']).first()
	print(customer)
	query = RentBook(bookId, customer.id, date.today().isoformat())

	# 밑에 명령어는 2개는 왜 에러가 발생하나요?
	# book_query = Books.query.filter(Books.id == bookId).update({'stock' : Books.stock - 1})
	# book_query = Books.query.filter_by(id = bookId).update({'stock' : Books.stock - 1})
	book_query = Book.query.filter_by(id = bookId).first()
	check_duplicattion = RentBook.query.filter(customer.id == RentBook.customer_id, RentBook.book_id == bookId).all()

	if book_query.stock > 0:
		if not check_duplicattion:
			book_query.stock -= 1
			# print(book_query)
			db.session.add(query)
			db.session.add(book_query)
			db.session.commit()
			db.session.close()
		else:
			flash('이미 대여중입니다.')
			return redirect(url_for('hello'))
	else:
		flash('재고가 없습니다.')
		return redirect(url_for('hello'))
	# redirect를 안하고, 대여하기 버튼을 누르면 책의 재고 수량만 바뀌고, 새로고침을 안하는 방법이 있나요? 리액트처럼 바뀐부분만 랜더링 하는...
	return redirect(url_for('hello'))


@app.route("/rent-log")
def rent_log():
	
	if 'log_in' in session:
		customer= User.query.filter_by(email = session['username']).first()
		rent_log = CheckInBook.query.filter(customer.id == CheckInBook.customer_id).all()
		rented_book = []
		date = []
		img = []
		
		for i in rent_log:
			rented_book.append(Book.query.filter(Book.id == i.book_id).all())
			date.append([i.rent_date, i.return_date])

		rented_book = sum(rented_book, [])

		for i in rented_book:
			img.append(i.id)
		# print(img, rented_book)
		return render_template('rental_log.html', books_info = rented_book, date=date, img=img)


@app.route("/checkin")
def checkin():
	
	if 'log_in' in session:
		customer= User.query.filter_by(email = session['username']).first()
		rent_log = RentBook.query.filter(customer.id == RentBook.customer_id).all()
		rented_book = []
		date = []
		img = []

		for i in rent_log:
			rented_book.append(Book.query.filter(Book.id == i.book_id).all())
			date.append([i.rent_date, i.return_date])

		rented_book = sum(rented_book, [])

		for i in rented_book:
			img.append(i.id)
	
		return render_template('checkin.html', books_info = rented_book, date=date, img=img)


@app.route("/checkin-book/<int:bookId>")
def checkin_book(bookId):
	customer= User.query.filter_by(email = session['username']).first()
	return_book = RentBook.query.filter(RentBook.customer_id == customer.id, RentBook.book_id == bookId).order_by(RentBook.id.desc()).first()
	left_log = CheckInBook(bookId, customer.id, return_book.rent_date, date.today().isoformat())
	# print(left_log)
	db.session.add(left_log)
	db.session.delete(return_book)
	db.session.commit()
	db.session.close()

	book_query = Book.query.filter_by(id = bookId).first()
	book_query.stock += 1
	db.session.add(book_query)
	db.session.commit()
	db.session.close()

	return redirect(url_for('checkin'))

if __name__ == "__main__":

	app.run(debug=True)
	csrf = CSRFProtect()
	csrf.init_app(app)