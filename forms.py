from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginF(FlaskForm):
    email = StringField("Email: ", validators=[Email("Ошибка email")])
    password = PasswordField("Пароль: ", validators=[DataRequired(),
                                                     Length(min=4, max=100,
                                                            message="Пароль от 4 до 100 символов")])
    remember = BooleanField("Запомнить меня", default=False)
    submit = SubmitField("Войти")


class RegisterF(FlaskForm):
    name = StringField("Имя: ", validators=[Length(min=4, max=30, message="Имя от 4 до 30 символов")])
    email = StringField("Email: ", validators=[Email("Ошибка email")])
    password = PasswordField("Пароль: ", validators=[DataRequired(),
                                                     Length(min=4, max=100,
                                                            message="Пароль от 4 до 100 символов")])

    password2 = PasswordField("Повтор пароля: ", validators=[DataRequired(),
                                                             EqualTo('password',
                                                                     message="Пароли не совпадают")])
    remember = BooleanField("Запомнить меня", default=False)
    submit = SubmitField("Регистрация")
