from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length


class RegistrationForm(FlaskForm):
    client_id = StringField('Client ID', validators=[DataRequired(), Length(min=1, max=200)])
    client_secret = PasswordField('Client Secret', validators=[DataRequired(), Length(min=1, max=200)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign in with Spotify')
