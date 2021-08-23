from app import db
from sqlalchemy.orm import relationship

class User(db.Model):
    
    __tablename__ = 'CUSTOMER'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    children = relationship("RentBook")

    # __init__을 쓰면 다른 곳에서 인스턴스에 인자값을 넘길 수 있다
    def __init__(self, username, email, password ):
        self.username = username
        self.email = email
        self.password = password

class Book(db.Model):
    __tablename__ = 'BOOK'

    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.Text(), nullable=False)
    publisher = db.Column(db.Text(), nullable=False)
    author = db.Column(db.String(20), nullable=False)
    publication_date = db.Column(db.Date, nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    isbn = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    link = db.Column(db.Text(), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Integer, nullable=False)
    children = relationship("RentBook")

    def __init__(self, stock, rate):
        self.stock = stock
        self.rate = rate
    
class RentBook(db.Model):
    __tablename__ = 'RENTAL_BOOK'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('BOOK.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('CUSTOMER.id'))
    rent_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=False)

    def __init__(self, book_id, customer_id, rent_date,return_date ):
        self.book_id = book_id
        self.customer_id = customer_id
        self.rent_date = rent_date
        self.return_date = return_date

# class rent book~~~
# 책 정보, 유저 정보
# 언제 빌렸는지, 언제 반납했는지
# fk 책이랑 유저
# sqlarchemy relationship 