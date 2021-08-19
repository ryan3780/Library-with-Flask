from app import db

class Users(db.Model):
    
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    email = db.Column(db.Text(), nullable=False)
    password = db.Column(db.String(20), nullable=False)

    # 초기화가 필요한지, 아래에 있는 클래스처럼 안쓰는게 맞는건지?
    def __init__(self, username, email, password ):
        self.username = username
        self.email = email
        self.password = password

class Books(db.Model):
    __tablename__ = 'books_table'

    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.Text(), nullable=False)
    publisher = db.Column(db.Text(), nullable=False)
    author = db.Column(db.String(20), nullable=False)
    publication_date = db.Column(db.Date, nullable=False)
    pages = db.Column(db.Integer, primary_key=False)
    isbn = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    link = db.Column(db.Text(), nullable=False)