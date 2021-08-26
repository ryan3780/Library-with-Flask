from flask import Flask, render_template, session, request, url_for, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import date, timedelta
from flask_wtf.csrf import CSRFProtect #csrf
from form import RegisterForm, CommentForm
import bcrypt
import math
import json

app = Flask(__name__)

app.secret_key = 'sample_secret_key'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost:3306/books_db" 
app.config['SQLALCHEMY_POOL_SIZE'] = 1
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
		page = request.args.get('page', type=int, default=1)
		books_info = Book.query.paginate(page, per_page=8 ,error_out=False)

		db.session.close()
		return render_template('main.html', books_info = books_info)
	else:
		return render_template('login.html', form= form)

@app.route("/login",  methods=['GET', 'POST'])
def login():
	form = RegisterForm()

	if 'log_in' in session:
		db.session.close()
		return redirect(url_for('main.html', form = form))

	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']

		password = password.encode('utf-8')
		data = User.query.filter_by(email = email).first()
		check_password = bcrypt.checkpw(password, data.password.encode('utf-8'))

		if data is not None and check_password:
			session['log_in'] = True
			session['email'] = email
			session['username'] = data.username
			db.session.close()

			return redirect(url_for('hello', form= form))

		flash('이메일과 비밀번호를 다시 입력해주세요.')	
		return redirect(url_for('hello', form= form))

@app.route("/logout")
def logout():
	session.pop('log_in', None)
	db.session.close()
	return redirect(url_for('hello'))


@app.route("/register", methods=['GET','POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		username = form.data.get('username')
		email = form.data.get('email')
		password = form.data.get('password')

		# username_validation = re.compile('^[가-힣a-zA-Z]+$')
		# email_validatioin = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
		# 최소 8자, 하나 이상의 문자, 하나의 숫자 및 하나의 특수 문자
		# pw_validation = re.compile('^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$')

		if len(password) < 8:
			flash('password는 8자 이상이여야합니다.')
			return render_template('register.html', form = form)

		if not any(char.isdigit() for char in password):
			flash('숫자가 포함되어야합니다.')
			return render_template('register.html', form = form)

		special_char = '`~!@#$%^&*()_+|\\}{[]":;\'?><,./'
		if not any(char in special_char for char in password):
			flash('특수문자가 포함되어야합니다.')
			return render_template('register.html', form = form)
		
		user = User.query.filter_by(email=email).first()
		if user:
			flash('이미 존재하는 유저입니다.')
			return render_template('signup.html')
		
		password = (bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())).decode('utf-8')
		query = User(username, email, password)
		# if bool(username_validation.match(username)) and bool(email_validatioin.match(email)) and bool(pw_validation.match(password)):
		db.session.add(query)
		db.session.commit()
		db.session.close()
		flash('가입을 정상적으로 완료했습니다.')
		return render_template('login.html', form = form)
	
	return 	render_template('register.html', form = form)

@app.route("/book-info/<int:bookId>", methods=['GET','POST'])
def detail(bookId):
	form = CommentForm()
	books_info = Book.query.filter(Book.id == bookId).all()
	total_comment = Comment.query.filter_by(book_id = bookId).order_by(Comment.id.desc()).all()
	customer= User.query.filter_by(email = session['email']).first()

	review = []

	for i in total_comment:
		customer = User.query.filter_by(id = i.customer_id).first()
		review.append([customer.username, i.content, i.rate])

	db.session.close()
	return render_template('book_info.html', books_info=books_info, form=form, comments = review)


@app.route("/rent-book/<int:bookId>") 
# ajax or main_page와 같은 주소로 처리 or 자바스크립트로 스크롤 위치 값 local storage로 저장해놨다가 불러와서 적용하기, '#' url 주소 뒤에 붙이는 방법 id 사용
def rent(bookId):
	customer= User.query.filter_by(email = session['email']).first()
	query = RentBook(bookId, customer.id, date.today().isoformat())
	book_query = Book.query.filter_by(id = bookId).first()
	check_duplicattion = RentBook.query.filter(customer.id == RentBook.customer_id, RentBook.book_id == bookId).all()

	if book_query.stock > 0:
		if not check_duplicattion:
			book_query.stock -= 1

			db.session.add(query)
			db.session.add(book_query)
			db.session.commit()
			db.session.close()
		else:

			flash('이미 대여중입니다.')
			return redirect(url_for('hello') + f'?page={math.ceil(bookId / 8)}')
	else:
		flash('재고가 없습니다.')
		return redirect(url_for('hello') + f'?page={math.ceil(bookId / 8)}')

	return redirect(url_for('hello') + f'?page={math.ceil(bookId / 8)}')


@app.route("/rent-log")
def rent_log():
	
	if 'log_in' in session:
		customer= User.query.filter_by(email = session['email']).first()
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

		db.session.close()
		return render_template('rental_log.html', books_info = rented_book, date=date, img=img)


@app.route("/checkin")
def checkin():
	
	if 'log_in' in session:
		customer= User.query.filter_by(email = session['email']).first()
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
	
		db.session.close()
		return render_template('checkin.html', books_info = rented_book, date=date, img=img)


@app.route("/checkin-book/<int:bookId>")
def checkin_book(bookId):
	customer= User.query.filter_by(email = session['email']).first()
	return_book = RentBook.query.filter(RentBook.customer_id == customer.id, RentBook.book_id == bookId).order_by(RentBook.id.desc()).first()
	left_log = CheckInBook(bookId, customer.id, return_book.rent_date, date.today().isoformat())

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


@app.route("/comment/<int:bookId>",  methods=['POST'])
def comment(bookId):
	form = CommentForm()
	customer= User.query.filter_by(email = session['email']).first()
	books_info = Book.query.filter(Book.id == bookId).all()
	total_comment = Comment.query.filter_by(book_id = bookId)
	book_rate = books_info[0]
	writed = Comment.query.filter_by(customer_id = customer.id, book_id = bookId).first()

	if request.method == 'POST':
		cc = form.data.get('content')
		rate = request.form['total']

		if writed:
			flash('댓글은 1개만 입력 가능합니다.')
			return redirect(url_for('detail', bookId=bookId))

		if len(cc) > 0 and rate != '' and writed == None:
			review = Comment(bookId, customer.id, cc, int(rate))
			db.session.add(review)

			total_rate = 0
			for i in total_comment:
				total_rate += int(i.rate)

			rate_avg = int(total_rate / len(total_comment.all()))
			book_rate.rate = rate_avg

			db.session.add(book_rate)
			db.session.commit()
			# db.session.close()
		else:
			flash('별점 입력해주세요')
			return redirect(url_for('detail', bookId=bookId))
	
	return redirect(url_for('detail', bookId=bookId))

if __name__ == "__main__":

	app.run(debug=True)
	csrf = CSRFProtect()
	csrf.init_app(app)