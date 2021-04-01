from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, HiddenField, FileField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from myproject.models import User


class LoginForm(FlaskForm):
    email = StringField('Email: ', validators=[DataRequired(), Email()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    email = StringField('Email: ', validators=[DataRequired(), Email()])
    username = StringField('Username: ', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired(), EqualTo('pass_confirm',
                                                                               message='Passwords must match')])
    pass_confirm = PasswordField('Confirm password: ', validators=[DataRequired()])

    submit = SubmitField('Register')

    def check_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has been already registered')

    def check_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is taken!')


class PostForm(FlaskForm):
    user_id = HiddenField()
    username = HiddenField()
    title = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Text', validators=[DataRequired()])
    submit = SubmitField('BlogPost')
    submit2 = SubmitField('Update')


class AccountForm(FlaskForm):
    old_username = HiddenField()
    new_username = StringField('Username', validators=[DataRequired(message='username field can\'t be empty')])
    email = StringField('Email', validators=[DataRequired(message='email field can\'t be empty')])
    img = FileField('Update profile picture')
    update = SubmitField('Update')



