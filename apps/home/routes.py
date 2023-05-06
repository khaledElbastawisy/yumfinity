# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask  import render_template, request, redirect, url_for, Flask, flash, abort
from flask_login import  login_required, current_user
from jinja2 import TemplateNotFound
from apps.authentication.models import *
from apps.authentication.forms import *
from werkzeug.utils import secure_filename
import os
from math import ceil
import random

# config for image upload
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "apps/static/assets/images/"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]




@blueprint.route('/index')
@login_required
def index():
    activities = get_followed_activities(current_user.id)
    followed_users = get_followed_users(current_user.id)
    feature_recipe, feature_recipe_author = recipe_of_the_day()
    return render_template('home/index.html', segment='index', activities = activities, followed_users = followed_users,
                            feature_recipe = feature_recipe, feature_recipe_author = feature_recipe_author) 

@blueprint.route('/browse_recipes')
@login_required
def browse_recipes():
    recipes = Recipe.query.all()
    recipes_per_page = 6
    page = request.args.get('page', 1, type=int)
    total_recipes = Recipe.query.count()
    total_pages = ceil(total_recipes / recipes_per_page)

    page_range = list(range(max(1, page - 2), min(total_pages, page + 2) + 1))

    recipes = Recipe.query.paginate(page, recipes_per_page, False).items

    favorite_recipes = UserProfile.query.filter_by(user_id=current_user.id).first().favorite_recipes
    cuisines = ['egyptian','american', 'chinese', 'french', 'italian', 'mexican', 'thai'] 
    return render_template('home/browse_recipes.html',  segment='browse_recipes', Recipes=recipes, page=page, total_pages=total_pages,
                            page_range=page_range, favorite_recipes=favorite_recipes, cuisines=cuisines)

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None


@blueprint.route('/recipe/<int:recipe_id>')
@login_required
def recipe_details(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    instructions = Instruction.query.filter_by(recipe_id=recipe_id).all()
    ingredients = Ingredient.query.filter_by(recipe_id=recipe_id).all()
    author = User.query.get(recipe.user_id)
    user = User.query.get(current_user.id)

    # calculate average rating
    rates = Rating.query.filter_by(recipe_id=recipe_id).all()
    if rates == []:
        avg_rate = None
    else:
        sum = 0
        for rate in rates:
            sum += rate.rating
        avg_rate = sum/len(rates)
    
    # check if user rated this recipe
    user_rating = Rating.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
    if user_rating:
        isRated = True
    else: isRated = False

    # get comments
    comments = Comment.query.filter_by(recipe_id=recipe_id).all()
    # Create a list of comments with the associated usernames
    def get_username(user_id):
        user = User.query.get(user_id)
        if user:
            return user.username
        else:
            return None
    comments_with_usernames = []
    for comment in comments:
        username = get_username(comment.user_id)
        comments_with_usernames.append({
            'username': username,
            'content': comment.content,
            'timestamp': comment.timestamp
        })

    isFollowing = Follow.query.filter_by(follower_id=current_user.id, followed_id=author.id).first()
    return render_template('home/recipe_detail.html', recipe=recipe, instructions = instructions,
                            ingredients = ingredients, author = author, rating = avg_rate, isRated=isRated,
                              comments = comments_with_usernames, user = user, rate_count = len(rates), isFollowing=isFollowing)



@blueprint.route('/recipe/rate_recipe', methods=['POST'])
@login_required
def rate_recipe():
    # Get form data
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()

    recipe_id = request.form.get('recipe_id')
    rate = request.form.get('rating')

    # Create a new Rating object
    rating = Rating(user_id=user.id, recipe_id=recipe_id, rating=rate)

    # Add the rating to the Rating table
    rating.save_to_db()

    # Redirect to the recipe details page
    return redirect(url_for('home_blueprint.recipe_details', recipe_id=recipe_id))

@blueprint.route('/recipe/submit_comment', methods=['POST'])
@login_required
def submit_comment():

    # Get form data
    recipe_id = request.form.get('recipe_id')
    comment = request.form.get('comment')

    # Create a new Rating object
    comment = Comment(user_id=current_user.id, recipe_id=recipe_id, content=comment)

    # Add the rating to the Rating table
    comment.save_to_db()




    # Redirect to the recipe details page
    return redirect(url_for('home_blueprint.recipe_details', recipe_id=recipe_id))


@blueprint.route('/create_recipe', methods=['GET', 'POST'])
@login_required
def create_recipe():
    form = RecipeForm()
    if request.method == 'POST' and form.validate():
        name = form.name.data
        cooking_time = form.cooking_time.data
        description = form.description.data
        cuisine = form.cuisine.data
        print (cooking_time)
        ingredientsList = form.ingredients.data.split('\n')

        instructionsList = form.instructions.data.split('\n')


        image = form.image.data
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save (os.path.join(os.path.abspath('.'), os.path.join(app.config["UPLOAD_FOLDER"], filename)))

        # Assuming the user is logged in and their ID is stored in a session variable
        new_recipe = Recipe(name=name, user_id=current_user.id, image = filename, cooking_time = cooking_time, description = description, cuisine = cuisine)
        new_recipe.save_to_db()

        # adding instructions
        for ingredient in ingredientsList:
            new_ingredient = Ingredient(name = ingredient, recipe_id = new_recipe.id)
            db.session.add(new_ingredient)
            db.session.commit()
        # adding ingredients
        for instruction in instructionsList:
            new_instruction = Instruction(method = instruction, recipe_id = new_recipe.id)
            db.session.add(new_instruction)
            db.session.commit()


        return redirect(url_for('home_blueprint.index'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
    return render_template('home/create_recipe.html', form=form)

@blueprint.route('/add_to_favorites/<int:recipe_id>', methods=['GET'])
@login_required
def add_to_favorites(recipe_id):
    # Get the user object
    user = current_user.id

    # Add the recipe to the user's favorites
    profile = UserProfile.query.filter_by(user_id=user).first()

    profile.add_to_favorites(recipe_id)

    # Save the changes to the database
    db.session.commit()

    print('added to favorites')
    print(profile.favorite_recipes)

    # Redirect to the same page, or to another page as desired
    return redirect(url_for('home_blueprint.browse_recipes'))

@blueprint.route('/search_results', methods=['GET'])
@login_required
def search_results():
    recipe_name = request.args.get('recipe_name', '')
    cuisine = request.args.get('cuisine', '')

    query = Recipe.query

    if recipe_name:
        query = query.filter(Recipe.name.ilike(f'%{recipe_name}%'))

    if cuisine:
        query = query.filter_by(cuisine=cuisine)

    recipes_per_page = 6
    page = request.args.get('page', 1, type=int)
    total_recipes = query.count()
    total_pages = ceil(total_recipes / recipes_per_page)

    page_range = list(range(max(1, page - 2), min(total_pages, page + 2) + 1))

    recipes = query.paginate(page, recipes_per_page, False).items
    recipes_count = len(recipes)    
    cuisines = ['egyptian','american', 'chinese', 'french', 'italian', 'mexican', 'thai'] 
    favorite_recipes = UserProfile.query.filter_by(user_id=current_user.id).first().favorite_recipes
    print(favorite_recipes)
    return render_template('home/browse_recipes.html', segment='search_results', Recipes=recipes, page=page, total_pages=total_pages,
                            page_range=page_range, favorite_recipes=favorite_recipes, recipes_count=recipes_count, cuisines = cuisines, searched = 1)

@blueprint.route('/follow_author', methods=['POST'])
@login_required
def follow_author():
    recipe_id = request.form.get('recipe_id')

    author_id = request.form.get('author_id')

    follow_action = Follow(follower_id = current_user.id, followed_id = author_id)
    db.session.add(follow_action)
    db.session.commit()
    # Your logic to follow the author goes here.
    # For example, save the follow action in the database.

    # Redirect back to the recipe details page or another appropriate page.

    return redirect(url_for('home_blueprint.recipe_details', recipe_id=recipe_id))


def get_followed_activities(user_id):

    # Get the IDs of followed users
    followed_users = Follow.query.filter_by(follower_id=user_id).all()

    # Extract the followed user IDs from the query result and return them as a list
    followed_users_ids = [follow.followed_id for follow in followed_users]

    # Get all activities of the followed users
    followed_activities = UserActivity.query.filter(
        UserActivity.user_id.in_(followed_users_ids)).order_by(
        UserActivity.timestamp.desc()).all()

    activities = []
    for activity in followed_activities:
        username = User.query.filter_by(id=activity.user_id).first().username
        recipe_name = Recipe.query.filter_by(id=activity.recipe_id).first().name

        activity_data = {
            'activity_type': activity.activity_type,
            'timestamp': activity.timestamp,
            'user_id': activity.user_id,
            'user_name': username,
        }

        if activity.activity_type == 'post':
            activity_data.update({
                'recipe_id': activity.recipe_id,
                'recipe_name': recipe_name,
            })

        elif activity.activity_type == 'rate':
            rating = Rating.query.filter_by(id=activity.rating_id).first().rating
            activity_data.update({
                'recipe_id': activity.recipe_id,
                'recipe_name': recipe_name,
                'rating': rating,
            })

        elif activity.activity_type == 'comment':
            comment_text = Comment.query.filter_by(id=activity.comment_id).first().content
            activity_data.update({
                'recipe_id': activity.recipe_id,
                'recipe_name': recipe_name,
                'comment_text': comment_text,
            })

        activities.append(activity_data)
    return activities

def get_followed_users(userid):
    followed_users = Follow.query.filter_by(follower_id=userid).all()
    followed_users_ids = [follow.followed_id for follow in followed_users]

    f_users = []
    for user in followed_users_ids:
        username = User.query.filter_by(id=user).first().username
        recipes_count = Recipe.query.filter_by(user_id=user).count()

        recipes_ids = [recipe.id for recipe in Recipe.query.filter_by(user_id=user).all()]
        ratings = Rating.query.filter(Rating.recipe_id.in_(recipes_ids)).all()
        avg_rating = None if not ratings else sum(rate.rating for rate in ratings) / len(ratings)
        
        user_data = {'username': username,
                    'recipes_count': recipes_count,
                     'avg_rating': avg_rating}
        
        f_users.append(user_data)
    print (f_users)
    return f_users


##########################################################################
@blueprint.route('/my_recipes', methods=['GET', 'POST'])
@login_required
def my_recipes():
    recipes = Recipe.query.filter_by(user_id= current_user.id).all()

    full_recipes_data = []
    for recipe in recipes:
        comments = Comment.query.filter_by(recipe_id=recipe.id).all()
        rates = Rating.query.filter_by(recipe_id=recipe.id).all()
        avg_rating = None if not rates else sum(rate.rating for rate in rates) / len(rates)
        instructions = Instruction.query.filter_by(recipe_id=recipe.id).all()
        ingredients = Ingredient.query.filter_by(recipe_id=recipe.id).all()

        full_recipes_data.append({
            'id': recipe.id,
            'name': recipe.name,
            'image': recipe.image,
            'cooking_time': recipe.cooking_time,
            'cuisine': recipe.cuisine,
            'comments': comments,
            'rate': avg_rating,
            'rate_count': len(rates),
            'instructions': instructions,
            'ingredients': ingredients
        })


    return render_template('home/my_recipes.html', recipes= full_recipes_data)




@blueprint.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    # Ensure the current user is the owner of the recipe
    if recipe.user_id != current_user.id:
        abort(403)

    form = RecipeForm()

    if request.method == 'POST' and form.validate():
        # Update recipe fields
        for field in ['name', 'cooking_time', 'description', 'cuisine']:
            setattr(recipe, field, getattr(form, field).data)

        # Update image if a new one is provided
        image = form.image.data
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            recipe.image = filename

        # Remove old ingredients and instructions
        for obj in Ingredient.query.filter_by(recipe_id=recipe.id).all() + Instruction.query.filter_by(recipe_id=recipe.id).all():
            db.session.delete(obj)
        db.session.commit()

        # Add new ingredients and instructions
        for cls, data in [(Ingredient, form.ingredients.data.split('\n')), (Instruction, form.instructions.data.split('\n'))]:
            for item in data:
                new_obj = cls(name=item, recipe_id=recipe.id) if cls == Ingredient else cls(method=item, recipe_id=recipe.id)
                db.session.add(new_obj)
        db.session.commit()
        flash('Recipe updated successfully.')

    if request.method == 'GET':
        for field in ['name', 'cooking_time', 'description', 'cuisine', 'image']:
            getattr(form, field).data = getattr(recipe, field)

        for cls, field in [(Ingredient, 'ingredients'), (Instruction, 'instructions')]:
            data = '\n'.join([getattr(obj, 'name' if cls == Ingredient else 'method') for obj in cls.query.filter_by(recipe_id=recipe.id).all()])
            getattr(form, field).data = data

    return render_template('home/edit_recipe.html', form=form, recipe=recipe)


@blueprint.route('/delete_recipe/<int:id>', methods=['POST'])
@login_required
def delete_recipe(id):

    recipe = Recipe.query.get_or_404(id)
    db.session.delete(recipe)
    db.session.commit()

    return redirect(url_for('home_blueprint.my_recipes'))

def recipe_of_the_day():
    recipes=Recipe.query.all()
    if recipes:
        random_recipe = random.choice(recipes)
        user=User.query.filter_by(id=random_recipe.user_id).first()
        username=user.username
    else:
        random_recipe = None
        username = None


    return random_recipe, username