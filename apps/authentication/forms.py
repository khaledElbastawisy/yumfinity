# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,TextAreaField, SelectField, IntegerField, RadioField
from wtforms.validators import Email, DataRequired, InputRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired


# login and registration


class LoginForm(FlaskForm):
    username = StringField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = StringField('Username',
                         id='username_create',
                         validators=[DataRequired()])
    email = StringField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])
    

    
class RecipeForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = TextAreaField('description', validators=[DataRequired()])
    ingredients = TextAreaField('ingredients', validators=[DataRequired()])
    instructions = TextAreaField('instructions', validators=[DataRequired()])
    image = FileField('image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'File type not allowed!')
    ])
        # Add the cuisine type drop-down menu
    cuisine = SelectField('cuisine', choices=[
        ('', 'Choose Cuisine'),
        ('egyptian', 'Egyptian'),
        ('american', 'American'),
        ('chinese', 'Chinese'),
        ('french', 'French'),
        ('indian', 'Indian'),
        ('italian', 'Italian'),
        ('mexican', 'Mexican'),
        ('thai', 'Thai'),
        ('other', 'Other'),
        # Add more cuisines as needed
    ], validators=[DataRequired()])
    
    # Add the cooking time input field (in minutes)
    cooking_time = IntegerField('cooking_time', validators=[DataRequired()])

class MealPlanForm(FlaskForm):
    day1 = RadioField('Day 1', validators=[InputRequired()], choices=['value'])
    day2 = RadioField('Day 2', validators=[InputRequired()], choices=['value'])
    day3 = RadioField('Day 3', validators=[InputRequired()], choices=['value'])
    day4 = RadioField('Day 4', validators=[InputRequired()], choices=['value'])
    day5 = RadioField('Day 5', validators=[InputRequired()], choices=['value'])
    day6 = RadioField('Day 6', validators=[InputRequired()], choices=['value'])
    day7 = RadioField('Day 7', validators=[InputRequired()], choices=['value'])