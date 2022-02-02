# app/forms.py
from app import models
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, DataRequired, Email, Length, Regexp, EqualTo, Optional, ValidationError


class RegisterForm(FlaskForm):
    """ User registration form"""
    firstname = StringField(validators=[InputRequired(), Length(3, 20, message="Please provide a valid first name"),
                                        Regexp("^[A-Za-z]*$", 0,"First names must have only letters")])
    surname = StringField(validators=[InputRequired(), Length(3, 20, message="Please provide a valid surname"),
                                      Regexp("^[A-Za-z]*$", 0, "Surnames must have only letters")])
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(8, 72)])
    cpwd = PasswordField(validators=[InputRequired(), Length(8, 72), EqualTo("pwd", message="Passwords must match !")])

    # THIS ISNT WORKING NEED TO FIX IT
    # def validate_name(self, firstname, surname):
    #     print(models.User.query.filter_by(FirstName=firstname.data, Surname=surname.data).first())
    #     if models.User.query.filter_by(FirstName=firstname.data, Surname=surname.data).first():
    #         raise ValidationError("Username already registered!")

    def validate_email(self, email):
        if models.User.query.filter_by(Email=email.data).first():
            raise ValidationError("Email already registered!")

class LoginForm(FlaskForm):
    """User login form"""
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    # Placeholder labels to enable form rendering
    username = StringField(
        validators=[Optional()]
    )

    def validate_email(self, email):
        if not models.User.query.filter_by(Email=email.data).first():
            raise ValidationError("Email not registered!")


class ResetPasswordRequestForm(FlaskForm):
    """User password reset request form"""
    email = StringField('Email', validators=[DataRequired(), Email()])

    def validate_email(self, email):
        if not models.User.query.filter_by(Email=email.data).first():
            raise ValidationError("Email not registered!")


class PasswordResetForm(FlaskForm):
    """User password reset form"""
    pwd = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    # Placeholder labels to enable form rendering
    cpwd = PasswordField(validators=[InputRequired(), Length(8, 72), EqualTo("pwd", message="Passwords must match !")])