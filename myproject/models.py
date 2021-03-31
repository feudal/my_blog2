import datetime
from myproject import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'user_table'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    img = db.Column(db.String(64))
    post = db.relationship("Post", backref='user', lazy=True)

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    __tablename__ = 'post_table'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    username = db.Column(db.String(64), index=True)
    time_created = db.Column(db.DateTime, default=datetime.datetime.now())
    text = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user_table.id'))

    def __init__(self, title, username, text, user_id):
        self.title = title
        self.username = username
        self.text = text
        self.user_id = user_id
