from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class PostForm(FlaskForm):
    """Form for creating and editing posts"""
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=3, max=120)
    ])
    content = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Upload Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    tags = StringField('Tags (comma separated)', validators=[
        Length(max=100)
    ])
    published = BooleanField('Publish', default=True)
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    """Form for adding comments to posts"""
    content = TextAreaField('Comment', validators=[
        DataRequired(),
        Length(min=1, max=500)
    ])
    submit = SubmitField('Post Comment')


class SearchForm(FlaskForm):
    """Form for searching posts"""
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')
