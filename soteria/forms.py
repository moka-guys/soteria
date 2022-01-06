from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length, Regexp, EqualTo, Optional, ValidationError
import models

class register_form(FlaskForm):
    firstname = StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="Please provide a valid first name"),
            Regexp(
                "^[A-Za-z]*$",
                0,
                "First names must have only letters",
            ),
        ]
    )
    surname = StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="Please provide a valid surname"),
            Regexp(
                "^[A-Za-z]*$",
                0,
                "Surnames must have only letters",
            ),
        ]
    )
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(8, 72)])
    cpwd = PasswordField(
        validators=[
            InputRequired(),
            Length(8, 72),
            EqualTo("pwd", message="Passwords must match !"),
        ]
    )
    def validate_name(self, firstname, surname):
        if models.User.query.filter_by(FirstName=firstname.data, Surname=surname.data).first():
            raise ValidationError("Username already registered!")

    def validate_email(self, email):
        if models.User.query.filter_by(Email=email.data).first():
            raise ValidationError("Email already registered!")

class login_form(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    # Placeholder labels to enable form rendering
    username = StringField(
        validators=[Optional()]
    )

class password_reset_form(FlaskForm):
    pwd = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    # Placeholder labels to enable form rendering
    cpwd = PasswordField(
        validators=[Optional()]
    )