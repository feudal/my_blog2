import os
import flask_login
from flask import render_template, redirect, url_for, flash, request
from flask.views import MethodView
from flask_login import login_user, login_required, logout_user

from myproject import app, db
from myproject.forms import LoginForm, RegistrationForm, PostForm, AccountForm
from myproject.models import User, Post
from flask_uploads import configure_uploads, IMAGES, UploadSet

app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOADED_IMAGES_DEST'] = 'myproject/static/img'

images = UploadSet('images', IMAGES)
configure_uploads(app, images)
basedir = os.path.abspath(os.path.dirname('__file__'))


@app.route('/')
def home():
    # posts = Post.query.all()
    posts = Post.query.order_by(Post.time_created.desc())
    return render_template('home.html', posts=posts)


@app.route('/post', methods=['GET', 'POST'])
def post():
    post_id = request.args.get('id_post')
    posts = Post.query.get(post_id)
    return render_template('post.html', post=posts)


@app.route('/about_us')
def about_us():
    return render_template('about_us.html')


@app.route('/logout')
@login_required
def log_out():
    logout_user()
    flash("You logged out!")
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def log_in():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None:
            flash("The email is wrong!")
            return render_template('login.html', form=form)

        if not user.check_password(form.password.data):
            flash("The password is wrong!")
            return render_template('login.html', form=form)

        login_user(user)
        flash('You logged successfully!')
        return redirect(url_for('home'))

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    user = User.query.filter_by(email=form.email.data).first()
    if user:
        flash("This email is in our base! Check if you wrote correctly!")
        return render_template('register.html', form=form)

    user = User.query.filter_by(username=form.username.data).first()
    if user:
        flash("This username is taken! Try another one!")
        return render_template('register.html', form=form)

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Thanks for registration!')
        return redirect(url_for('log_in'))

    return render_template('register.html', form=form)


class Account(MethodView):
    decorators = [login_required]

    def get(self):
        form = AccountForm()
        return render_template('account.html', form=form)

    def post(self):
        form = AccountForm()
        user_object = User.query.filter_by(username=flask_login.current_user.username).first()
        old_username = user_object.username
        new_username = form.new_username.data
        old_email = user_object.email
        new_email = form.email.data

        username_message = self.check_change_user(old_username, new_username, user_object)
        email_message = self.check_change_email(old_email, new_email, user_object)

        if username_message == 'name is in the db' or email_message == 'email is in the db':
            flash('The name/email is taken!')
            return render_template('account.html', form=form)

        img_message = self.check_change_img(user_object, form)

        print(username_message, email_message, img_message)

        # message generating
        if username_message == 'not changed' and email_message == 'not changed' and img_message == 'not changed':
            return render_template('account.html', form=form)
        if username_message == 'has changed' and email_message == 'not changed' and img_message == 'not changed':
            flash('Username changed successfully!')
            return render_template('account.html', form=form)
        if username_message == 'not changed' and email_message == 'has changed' and img_message == 'not changed':
            flash('Email changed successfully!')
            return render_template('account.html', form=form)
        if username_message == 'not changed' and email_message == 'not changed' and img_message == 'has changed':
            flash('Image uploaded successfully!')
            return render_template('account.html', form=form)

        flash('Information changed successfully!')
        return render_template('account.html', form=form)

    def check_change_user(self, o_user, n_user, user_obj):
        if o_user == n_user:
            return 'not changed'
        if Post.query.filter_by(username=n_user) is None:
            return 'name is in the db'

        user_obj.username = n_user
        user_posts = Post.query.filter_by(username=o_user)
        # change name in posts
        for his_post in user_posts:
            his_post.username = n_user
        db.session.commit()
        return 'has changed'

    def check_change_email(self, o_email, n_email, user_obj):
        if o_email == n_email:
            return 'not changed'
        if Post.query.filter_by(username=n_email) is None:
            return 'email is in the db'
        user_obj.email = n_email
        db.session.commit()
        return "has changed"

    def check_change_img(self, user_obj, form):
        if not form.img.data:
            return 'not changed'

        old_filename = user_obj.img
        db.session.commit()
        # delete old file
        if old_filename:
            path_to_img = basedir + '\myproject\static\img\\' + old_filename
            os.remove(path_to_img)

        new_filename = images.save(form.img.data)  # save img in the folder img
        user_obj.img = new_filename
        db.session.commit()

        return 'has changed'


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        username = flask_login.current_user.username
        user = User.query.filter_by(username=username).first()
        post = Post(form.title.data, username, form.text.data, user.id)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!')

        return redirect(url_for('home'))

    return render_template('create.html', form=form)


@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    post_id = request.args.get('id_post')
    posts = Post.query.get(post_id)

    form = PostForm()
    if not form.validate_on_submit():
        form.text.data = posts.text
        form.title.data = posts.title

    if form.validate_on_submit():
        my_post = Post.query.get(post_id)
        my_post.title = form.title.data
        my_post.text = form.text.data
        db.session.commit()
        flash('Post updated successfully')

        return redirect(url_for('home'))

    return render_template('update.html', form=form, posts=posts)


@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    post_id = request.args.get('id_post')
    Post.query.filter_by(id=post_id).delete()
    db.session.commit()
    flash('Post deleted successfully')

    return redirect(url_for('home'))


app.add_url_rule('/account', view_func=Account.as_view('account'))

if __name__ == '__main__':
    app.run(debug=True)
