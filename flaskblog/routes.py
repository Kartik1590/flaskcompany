from datetime import datetime as dt
from flaskblog import app,db,bcrypt
from flask import jsonify, render_template,flash,redirect,url_for,request
from flaskblog.models import Post, Provision,User
from flaskblog.forms import Login,Register,UpdateAccountForm,PostForm
from flask_login import login_user,current_user,logout_user,login_required
import json
import secrets,os
from PIL import Image
# posts=[
    # {
    #     'author':"Honey Choudhari",
    #     "title":"Js",
    #     "content":"js content",
    #     "date_posted":dt.strftime(dt.now(),format="%d/%m/%y")
    # },
    # {
    #     'author':"Kartik Choudhari",
    #     "title":"python",
    #     "content":"python content",
    #     "date_posted":dt.strftime(dt.now(),format="%d/%m/%y")
    # }
# ]
@app.route("/")
@app.route('/home')
def home():
    posts=Post.query.all()
    return render_template('home.html',posts=posts)

@app.route('/about')
def about():
    return render_template('about.html',title='about')

@app.route('/register',methods=['POST','GET'])
def Registeration():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form =Register()
    print(form)
    if form.validate_on_submit() and request.method=='POST':
        hash_pass=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data,email=form.email.data,password=hash_pass)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}','success')
        return redirect(url_for('login'))
    # if request.method=="POST":
    #     data=request.form
    #     print(data)
    return render_template('register.html',title="register",form=form)
@app.route('/login',methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form =Login()
    if request.method=='POST' and form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            password=bcrypt.check_password_hash(user.password,form.password.data)
        if user and password:
            login_user(user,remember=form.remember.data)
            # flash(f'Welcome {form.email.data} enjoy', 'success')
            next_page=request.args.get('next')

            return redirect(url_for('account')) if next_page else redirect(url_for('home'))
        else:
            flash(f'Please check your email and password','danger')
    return render_template('login.html',title="login",form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.path.splitext(form_picture.filename)
    picture_fn=random_hex+f_ext
    picture_path=os.path.join(app.root_path,'static/pics',picture_fn)
    output_size=(125,125)
    image=Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)
    return picture_fn
@app.route('/account',methods=['GET','POST'])
@login_required
def account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file=save_picture(form.picture.data)
            current_user.image_file=picture_file
        current_user.username=form.username.data
        current_user.email=form.email.data
        # current_user.image_file=form.picture.data
        db.session.commit()
        flash('You profile has been updated successfully','success')

        return redirect(url_for('account'))
    elif request.method=='GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
    image_url=url_for('static',filename="pics/"+current_user.image_file)
    return render_template('account.html',title='account',image_file=image_url,form=form)


@app.route("/post/new",methods=['GET','POST'])
@login_required
def new_post():
    form=PostForm()
    if form.validate_on_submit():
        post=Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post has been created','success')
        return redirect(url_for('home'))
    return render_template('create_post.html',title='New Post',form=form)

@app.route('/post/<int:post_id>')
def post(post_id):
    post=Post.query.get_or_404(post_id)
    return render_template('post.html',title=post.title,post=post)

@app.route('/catalog',methods=['POST','GET'])
def catalog():
    
    if request.method=='POST':
        return redirect(url_for('home'))
    return render_template('catalog.html')

@app.route('/get_tenant')
def get_tenant():
    data=Provision.query.all()
    data=[d.tenant for d in data]
    data=list(set(data))
    return jsonify(data)

@app.route('/get_env',methods=['POST'])
def get_env():
    if request.method=="POST":

        req=request.get_json()
        print(type(req))
        data=Provision.query.filter(Provision.tenant==req['tenant']).all()
        data=[d.environment for d in data]
        data=list(set(data))
        return jsonify({"message": "Success","env":data})
    
@app.route('/get_loc',methods=['POST'])
def get_loc():
    if request.method=="POST":

        req=request.get_json()
        print(req)
        data=Provision.query.filter((Provision.tenant==req['tenant']) & (Provision.environment==req['env'])).all()
        data=[d.location for d in data]
        data=list(set(data))
        return jsonify({"message": "Success","loc":data})
    
@app.route('/get_manage',methods=['POST'])
def get_manage():
    if request.method=="POST":

        req=request.get_json()
        print(req)
        data=Provision.query.filter((Provision.tenant==req['tenant']) & (Provision.environment==req['env']) & (Provision.location==req['loc'])).all()
        data=[d.management for d in data]
        data=list(set(data))
        return jsonify({"message": "Success","manage":data})
@app.route('/get_subtype',methods=['POST'])
def get_subtype():
    if request.method=="POST":

        req=request.get_json()
        print(req)
        data=Provision.query.filter((Provision.tenant==req['tenant']) & (Provision.environment==req['env']) & (Provision.location==req['loc']) & (Provision.management==req['manage'])).all()
        data=[d.subtype for d in data]
        data=list(set(data))
        return jsonify({"message": "Success","subtype":data})
    
@app.route('/get_app',methods=['POST'])
def get_app():
    if request.method=="POST":

        req=request.get_json()
        print(req)
        data=Provision.query.filter((Provision.tenant==req['tenant']) & (Provision.environment==req['env']) & (Provision.location==req['loc']) & (Provision.management==req['manage']) & (Provision.subtype==req['subtype'])).all()
        print(data)
        data=[d.application for d in data]
        print(data)
        data=list(set(data))
        return jsonify({"message": "Success","apps":data})
@app.route('/get_data',methods=['POST'])
def get_data():
    if request.method=="POST":

        req=request.get_json()
        print(req)
        data=Provision.query.filter((Provision.tenant==req['tenant']) & (Provision.environment==req['env']) & (Provision.location==req['loc']) & (Provision.management==req['manage']) & (Provision.subtype==req['subtype']) & (Provision.application==req['app'])).all()
        data=[{'rg':d.rg,'sub':d.subscription,'vnet':d.vnet,'subnet':d.subnet} for d in data]
        # print(data)
        # data=list(set(data))
        return jsonify({"message": "Success","data":data})
    
