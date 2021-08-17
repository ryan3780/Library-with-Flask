from flask import Flask, render_template, session, request, url_for, redirect

app = Flask(__name__)
app.secret_key = 'sample_secret_key'
admin = {'admin': '1234'}


@app.route("/")
def hello():
	if 'log_in' in session:
		return render_template('base.html')
	else:
		return render_template('login.html')

@app.route("/login", methods=['POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		for id, pwd in admin.items():
			if username == id and password == pwd:
				session['log_in'] = True
				session['username'] = username
				return render_template('base.html')
			else:
				return '''<script>alert('nonono');location.href='/';</script>'''

@app.route("/logout")
def logout():
	session.pop('log_in', None)
	return redirect(url_for('hello'))

@app.route("/register", methods=['GET','POST'])
def register():
	return 	render_template('register.html')

if __name__ == "__main__":
	app.run(debug=True)