from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Optional, ValidationError
from flask_wtf.file import FileField, FileAllowed
from sqlalchemy import func
from ssn.models import User, Post
from flask_login import current_user


class CommentForm(FlaskForm):
    content = TextAreaField('Your Comment', validators=[DataRequired()])
    submit = SubmitField('Add Comment')


class EditCommentForm(FlaskForm):
    content = TextAreaField('Your Comment', validators=[DataRequired()])
    submit = SubmitField('Update')


class SearchForm(FlaskForm):
    target = StringField(validators=[DataRequired()])
    submit = SubmitField('Search')

    def validate_post(self, target):
        post = Post.query.filter(func.lower(Post.content).contains(target.data.lower())).first() or True
        if not post:
            raise ValidationError('Not found!')

    def validate_user(self, target):
        user = User.query.filter(func.lower(User.username).contains(target.data.lower())).first() or True
        if not user:
            raise ValidationError('Not found!')


class MessageForm(FlaskForm):
    body = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    post_image = FileField('Image', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'svg'])])
    submit = SubmitField('Post')


class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    post_image = FileField('Image', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'svg'])])
    submit = SubmitField('Update')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Oops, that email address already taken, please choose a different one')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone')
    date_of_birth = DateField('Date of birth', format='%d.%m.%Y', validators=[Optional()])
    status = StringField('Status', validators=[Length(max=100)])
    profile_img = FileField('Profile Image', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'svg'])])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if current_user.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Oops, that email address already taken, please choose a different one')
