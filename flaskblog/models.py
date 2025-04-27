from flaskblog import db,login_manager
from datetime import datetime as dt
from flask_login import UserMixin
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    image_file=db.Column(db.String(20),default='default.jpg')
    password=db.Column(db.String(60),nullable=False)
    posts=db.relationship('Post',backref='author',lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"
    
class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    date_posted =db.Column(db.DateTime,nullable=False,default=dt.now)
    content=db.Column(db.Text,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    def __repr__(self):
        return f"Post('{self.title}')"
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    subscription=db.Column(db.String(100),nullable=False)
    resourcegroup=db.Column(db.String(100),nullable=False)
    def __repr__(self):
        return f"Post('{self.title}')"
class Test2(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    subscription=db.Column(db.String(100),nullable=False)
    vm=db.Column(db.String(100),nullable=False)
    def __repr__(self):
        return f"Post('{self.title}')"
    
class Provision(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    tenant=db.Column(db.String(40),nullable=False)
    environment=db.Column(db.String(40),nullable=False)
    location=db.Column(db.String(40),nullable=False)
    management=db.Column(db.String(40),nullable=False)
    subtype=db.Column(db.String(40),nullable=False)
    application=db.Column(db.String(40),nullable=False)
    subscription=db.Column(db.String(40),nullable=False)
    vnet=db.Column(db.String(40),nullable=False)
    rg=db.Column(db.String(40),nullable=False)
    subnet=db.Column(db.String(40),nullable=False)

    def __repr__(self):
        return f"Provision('{self.tenant}')"
class RitmRecord(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    ritm_number=db.Column(db.String(255),nullable=False)
    payload=db.Column(db.Text,nullable=False)


