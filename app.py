import os
import flask_login
from flask import render_template, redirect, url_for, flash, request
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

        try:
            if user.check_password(form.password.data) and user is not None:
                login_user(user)
                flash("Logged in Successfully!")
        except AttributeError:
            flash("Wrong password or login")
            return render_template('login.html', form=form)

        return redirect(url_for('home'))

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Thanks for registration!')
        return redirect(url_for('log_in'))

    return render_template('register.html', form=form)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = AccountForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.old_username.data).first()
        #  will change the name of the user only if the new name isn't in db
        if not User.query.filter_by(username=form.new_username.data).first():
            # change the name in all posts
            username_in_posts = Post.query.filter_by(username=user.username)
            for my_post in username_in_posts:
                my_post.username = form.new_username.data

            user.username = form.new_username.data
            user.email = form.email.data
        else:
            flash('Chose another name because this name is taken!')

        if form.img.data:  # if file is uploaded
            filename = images.save(form.img.data)
            # path to the img directory
            path_to_img = basedir + '/myproject/static/img/'
            new_filename = str(user.id)+(os.path.splitext(filename)[-1])
            if os.path.isfile(os.path.join(path_to_img, new_filename)):
                print('delete')
                os.remove(os.path.join(path_to_img, new_filename))

            os.rename(os.path.join(path_to_img, filename), os.path.join(path_to_img, new_filename))
            # the name of photo field will be like the id of the user + extension
            user.img = new_filename

            db.session.commit()

        flash('Account updated! Press Ctr+F5, if you upload photo!')

        return render_template('account.html', form=form)

    return render_template('account.html', form=form)


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


if __name__ == '__main__':
    app.run(debug=True)
