from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms.validators import DataRequired, EqualTo, Email

class RegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired(), EqualTo('password_2')])
    password_2 = PasswordField('repassword', validators=[DataRequired()])


class CommentForm(FlaskForm):
    content = StringField('comment', validators=[DataRequired()])