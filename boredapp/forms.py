from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, EmailField, DateField
from wtforms.validators import DataRequired


# Form for sign up
class SignUpForm(FlaskForm):
    """
        This class creates a submission form for the user sign up
    """
    firstname = StringField("Firstname:", validators=[DataRequired()])
    lastname = StringField("Lastname", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    dateofbirth = DateField("Date Of Birth", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up")


# Form for log in
class LogInForm(FlaskForm):
    """
        This class creates a submission form for the user log in
    """
    emailOrUsername = StringField("emailOrUsername:", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


# Form for forgot password
class ForgotPassword(FlaskForm):

    """
        This class creates a submission form for the user forgot password form
    """
    emailOrUsername = StringField("emailOrUsername:", validators=[DataRequired()])
    submit = SubmitField("Reset Password")
