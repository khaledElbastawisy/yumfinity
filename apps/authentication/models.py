# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin, login_required, current_user
from apps import db, login_manager
from apps.authentication.util import hash_pass
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import event


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    follower = db.relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed = db.relationship("User", foreign_keys=[followed_id], back_populates="followers")

class User(db.Model, UserMixin):

    #__tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)

    recipes = db.relationship('Recipe', backref='user')
    ratings = db.relationship('Rating', backref='user')
    comments = db.relationship('Comment', backref='user')

    profile = db.relationship("UserProfile", uselist=False, back_populates="user")
    activities = db.relationship('UserActivity', back_populates='user', lazy=True)
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], back_populates='followed', lazy='dynamic', cascade='all, delete-orphan')
    following = db.relationship('Follow', foreign_keys=[Follow.follower_id], back_populates='follower', lazy='dynamic', cascade='all, delete-orphan')
    shopping_list = db.relationship('ShoppingList', backref='user', lazy=True, cascade='all, delete-orphan')
    meal_plan = db.relationship('MealPlan', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)

class Recipe(db.Model):

    #__tablename__ = 'Recipe'

    id = db.Column(db.Integer, primary_key=True)
    cuisine = db.Column(db.String(64))
    name = db.Column(db.String(64))
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cooking_time = db.Column(db.Integer, nullable=False)
    cuisine = db.Column(db.String(64), nullable=False)
    image = db.Column(db.String(255), nullable=True)

    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True, cascade='all, delete-orphan')
    instructions = db.relationship('Instruction', backref='recipe', lazy=True, cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='recipe', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='recipe', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('UserActivity', back_populates='recipe', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]


            setattr(self, property, value)
    
    def create_activity(self):
        activity = UserActivity(activity_type='post', user_id=self.user_id, recipe_id=self.id)
        db.session.add(activity)
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        self.create_activity()
    

    def __repr__(self):
        return str([str(self.id),str(self.cuisine),str(self.name),str(self.ratings),str(self.comments),str(self.user_id)])

class Instruction(db.Model):
    
    #__tablename__ = 'Instruction'
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(), unique=False, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

    def __init__(self, **kwargs):

        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]


            setattr(self, property, value)


class Ingredient(db.Model):
    #__tablename__ = 'Ingredient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

    def __init__(self, **kwargs):

        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]


            setattr(self, property, value)

class Rating(db.Model):
    #__tablename__ = 'Rating'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    activities = db.relationship('UserActivity', back_populates='rating', lazy=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]


            setattr(self, property, value)

    def create_activity(self):
        activity = UserActivity(activity_type='rate', user_id=self.user_id, rating_id=self.id, recipe_id=self.recipe_id)
        db.session.add(activity)
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        self.create_activity()




class Comment(db.Model):
    #__tablename__ = 'Comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    activities = db.relationship('UserActivity', back_populates='comment', lazy=True)
    
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, property, value)

    def create_activity(self):
        activity = UserActivity(activity_type='comment', user_id=self.user_id, comment_id=self.id, recipe_id=self.recipe_id)
        db.session.add(activity)
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        self.create_activity()



class UserProfile(db.Model):
    #__tablename__ = 'UserProfile'
    id = db.Column(db.Integer, primary_key=True)
    biography = db.Column(db.Text)
    
    @declared_attr
    def user_id(cls):
        return db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)

    @declared_attr
    def user(cls):
        return db.relationship("User", back_populates="profile")

    favorite_recipes_str = db.Column(db.String, nullable=True)
    
    @property
    def favorite_recipes(self):
        # Convert comma-separated string of favorite_recipe_ids to a list of integers
        if self.favorite_recipes_str:
            return [int(recipe_id) for recipe_id in self.favorite_recipes_str.split(',')]
        return []

    @favorite_recipes.setter
    def favorite_recipes(self, recipe_ids):
        # Convert list of integers to a comma-separated string
        self.favorite_recipes_str = ','.join(str(recipe_id) for recipe_id in recipe_ids)

    def add_to_favorites(self, recipe_id):
        # Check if the recipe_id is not already in the favorite_recipes list
        if recipe_id not in self.favorite_recipes:
            # Add the recipe_id to the favorite_recipes list
            current_favorites = self.favorite_recipes
            current_favorites.append(recipe_id)

            # Update the favorite_recipe_ids column with the new list
            self.favorite_recipes = current_favorites
    
    def remove_from_favorites(self, recipe_id):
        # Check if the recipe_id is in the favorite_recipes list
        if recipe_id in self.favorite_recipes:
            # Remove the recipe_id from the favorite_recipes list
            current_favorites = self.favorite_recipes
            current_favorites.remove(recipe_id)

            # Update the favorite_recipe_ids column with the new list
            self.favorite_recipes = current_favorites
    


class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", back_populates="activities")

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=True)
    recipe = db.relationship("Recipe", back_populates="activities")

    rating_id = db.Column(db.Integer, db.ForeignKey('rating.id'), nullable=True)
    rating = db.relationship("Rating", back_populates="activities")

    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    comment = db.relationship("Comment", back_populates="activities")


    
    def add_activity(self, user_id, activity_type, recipe_id=None, rating_id=None, comment_id=None):
        self.user_id = user_id
        self.activity_type = activity_type
        self.time_stamp = datetime.now()
        self.recipe_id = recipe_id

        if activity_type == 'post_recipe':
            return
        elif activity_type =='rate':
            self.rating_id = rating_id
            return
        elif activity_type =='comment':
            self.comment_id = comment_id
            return
        else:
            raise ValueError('Invalid activity_type')

class ShoppingList(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item = db.Column(db.String(64), nullable=False)




    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

class MealPlan(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meal1_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    meal2_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    meal3_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    meal4_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    meal5_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    meal6_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    meal7_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def get_recipe(self,meal_id):
        return Recipe.query.filter_by(id=meal_id)
    
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]
            setattr(self, property, value)


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None

