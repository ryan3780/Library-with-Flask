from flask import Flask, render_template, session, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

admin = {'admin': '1234'}

app = Flask(__name__)
app.secret_key = 'sample_secret_key'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost:3306/books_db" 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db 연결 부분 코치님께 이렇게 연결하는게 맞는건지, 더 좋은 방법이 없는지, 각 라우터 마다 필요한 테이블의 이름을 수정하면서 써야하는지...
engine = create_engine('mysql+pymysql://root:root@localhost:3306/books_db')
db = SQLAlchemy(app)
db.init_app(app)
db.create_all()

con = engine.connect()
metadata = db.MetaData()
table = db.Table('customers', metadata, autoload=True, autoload_with=engine)
# print(db.select([table]))
# print(table.select().where(table.c.email == 1))

# email을 출력하려면 몇번째 자리인지 알아야 하는데, table.email 이런 형식으로 불러 오지 못하나?

@app.route("/")
def hello():
	if 'log_in' in session:
		return render_template('base.html')
	else:
		return render_template('login.html')

@app.route("/login", methods=['POST'])
def login():
	con = engine.connect()
	metadata = db.MetaData()
	table = db.Table('customers', metadata, autoload=True, autoload_with=engine)

	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		query = table.select()
		res = con.execute(query).fetchall()
		
		# db에 있는 고객정보를 받아와서 비교해서 if/else문으로 구분하려고 하는데, else를 쓰면 두번째 아이디 부터는 다 else로 빠져버립니다.
		for customer in res:
			print(customer)
			print(username, password)
			if username == customer[2] and password == customer[3] :
				session['log_in'] = True
				session['username'] = username
				return render_template('base.html')
			# else:
			# 	return '''<script>alert('nonono'); location.href= '/';</script>''' 
			
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

		if password == check:
			con = engine.connect()
			metadata = db.MetaData()
			table = db.Table('customers', metadata, autoload=True, autoload_with=engine)
			con.execute(table.insert(), username=username, email= email, password=password)
			
			return render_template('login.html')

	return 	render_template('register.html')

if __name__ == "__main__":
	app.run(debug=True)