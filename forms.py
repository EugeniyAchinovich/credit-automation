from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField
from wtforms.validators import DataRequired, Email, Length


class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField('Зарегистрироваться')


class LoanApplicationForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    amount = FloatField('Сумма кредита', validators=[DataRequired()])
    interest_rate = FloatField('Процентная ставка (%)', validators=[DataRequired()])
    submit = SubmitField('Подать заявку')


class LoginForm(FlaskForm):
    email = StringField('Эл. почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')