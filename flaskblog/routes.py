from datetime import datetime as dt
from flaskblog import app,db,bcrypt,api
from flask import jsonify, render_template,flash,redirect,url_for,request,abort
from flask_restful import Api,Resource,reqparse
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt_identity
from flaskblog.models import Post, Provision,User,RitmRecord
from flaskblog.forms import Login,Register,UpdateAccountForm,PostForm
from flask_login import login_user,current_user,logout_user,login_required
import json
import zlib,base64,ast
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
@login_required
def post(post_id):
    post=Post.query.get_or_404(post_id)
    return render_template('post.html',title=post.title,post=post)
@app.route('/post/<int:post_id>/update',methods=['GET','POST'])
def update_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form=PostForm()
    
    if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data
        db.session.commit()
        flash('Post has been updated','success')
        return redirect(url_for('home'))
    form.title.data=post.title
    form.content.data=post.content
    return render_template('create_post.html',title="Update post",form=form)

@app.route('/post/<int:post_id>/delete',methods=['GET','POST'])
def delete_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post has been deleted','success')
    return redirect(url_for('home'))


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
    
users={
    "testuser":"testpassword"
}

class LoginApi(Resource):
    def post(self):
        username=request.json.get('username')
        password=request.json.get('password')
        if not username or not password:
            return {"message":"Username and Password required"},400
        
        if users.get(username)==password:
            access_token=create_access_token(identity=username)
            return {"access_token":access_token},200
        else:
            return {"message":"Invalid credentials"},401
        
# class Protected(Resource):
#     @jwt_required()
#     def get(self):
#         current_user=get_jwt_identity()
#         user_data=[i.username for i in User.query.all()]
#         if request.args.get('action')=='list':
#             return {
#                 "message":f"Yes its working...",
#                 "Value":[{"Username":i.username,"Email":i.email} for i in User.query.all()]
#             },200
#         if request.args.get('username') in user_data:
#             user_name=request.args.get('username')
#             user_name_data=User.query.filter(User.username==user_name).first()
#             print(user_name_data)
#             return {
#                 "Value":{"Username":user_name_data.username,"Email":user_name_data.email}
#             },200
#         return {
#             "message":f"Hello,{current_user} you have passed wrong query",
#         },400
#     def get(self,username):
#         user_name_data=User.query.filter_by(username=username).first()
#         {
#             "Value":{
#                 "Username":user_name_data.username,
#                 "Email":user_name_data.email
#             }
#         },200
#Overridding doesn't work here so don't do this mistake.

class Protected(Resource):
    @jwt_required()
    def get(self,username=None):
        current_user=get_jwt_identity()
        action=request.args.get('action')
        user_name=request.args.get('username')
        if username:
            return self.get_user_by_username(username)
        
        if action == 'list':
            return self.list_all_users()
        
        if user_name:
            return self.get_user_by_query(user_name)
        
        return self.bad_request(current_user)
    
    def get_user_by_username(self,username):
        user=User.query.filter_by(username=username).first()
        if user:
            return {
                "Value":{
                    "Username":user.username,
                    "Email":user.email
                }
            },200
        else:
            return {
                "message":f"No user found with the username {username}"
            },404
    
    def list_all_users(self):
        
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 3))
            if page < 1 or limit < 1:
                raise ValueError
        except ValueError:
            return self.success_response(data=None, message="Page and limit must be positive integers", status_code=400)
        
        sort_by=request.args.get('sort_by','username')
        order=request.args.get('order','asc')
        search=request.args.get('search',None)
        allowed_sort_fields=['username','email']
        if sort_by not in allowed_sort_fields:
            return self.success_response(data=None,message=f"sort_by must be one of {allowed_sort_fields}",status_code=400)
        sort_field=getattr(User,sort_by)
        if order=='desc':
            sort_field=sort_field.desc()
        else:
            sort_field=sort_field.asc()
        offset=(page-1)*limit
        query=User.query
        if search:
            search =f"%{search}%"
            query=query.filter(User.username.ilike(search))

        users=query.order_by(sort_field).offset(offset).limit(limit).all()
        user_list=[{"Username":user.username,"Email":user.email} for user in users]
        total_users=query.count()
        extra={
            "pagination":{
                "current_page":page,
                "limit":limit,
                "total_users":total_users,
                "total_page":(total_users+limit-1)//limit
            },
            "sorting":{
                "sorted_by":sort_by,
                "order":order
            },
            "search": search if search else None
        }
        return self.success_response(data=user_list,extra=extra)
        # return {
        #     "message":"List of all the users",
        #     "Value":user_list
        # },200
    def get_user_by_query(self,user_name):
        user=User.query.filter_by(username=user_name).first()
        if user:
            data={
                    "Username":user.username,
                    "Email":user.email
                }
            return self.success_response(data=data)
            # return {
            #     "Value":{
            #         "Username":user.username,
            #         "Email":user.email
            #     }
            # },200
        else:
            fail_message=f"No user found with username '{user_name}'"
            return self.success_response(data=fail_message,message="Failed",status_code=404)
    def bad_request(self,current_user):
        return {
            "message":f"Hello, {current_user}. You have passed wrong query or parameter"
        },400
        
    def success_response(self,data,message="Success",status_code=200,extra=None):
        response={
            "message":message,
            "data":data
        }
        if extra:
            response.update(extra)
        return response,status_code

class RitmResource(Resource):
    @jwt_required()
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument('ritm_number',type=str,required=True,help="RITM number is required")
        parser.add_argument('payload',type=str,required=True,help="Payload is required")
        data=parser.parse_args()
        compressed_payload=zlib.compress(data['payload'].encode('utf-8'))
        compressed_payload_b64=base64.b64encode(compressed_payload).decode('utf-8')
        new_record=RitmRecord(
            ritm_number=data['ritm_number'],
            payload=compressed_payload_b64
        )
        db.session.add(new_record)
        db.session.commit()

        get_data=RitmRecord.query.filter_by(ritm_number=data['ritm_number']).first()
        final_data={
            "Id":get_data.id,
            "Ritm Number":get_data.ritm_number,
            
        }
        return {
            "message":"Record created Successfully",
            "Data":final_data
        },201
    

    @jwt_required()
    def get(self):
        ritm_number=request.args.get('ritm')
        record=RitmRecord.query.filter_by(ritm_number=ritm_number).first()
        if not record:
            return {
                "message":f"Record not found for {ritm_number}"
            },404
        compressed_payload=base64.b64decode(record.payload)
        original_payload=zlib.decompress(compressed_payload).decode('utf-8')
        ori_payload=ast.literal_eval(original_payload)

        return {
            "ritm_number":record.ritm_number,
            "payload":ori_payload
        },200
        
    
api.add_resource(LoginApi,'/login_api')
# api.add_resource(Protected,'/protected')
api.add_resource(Protected,'/protected/username/<string:username>','/protected')
api.add_resource(RitmResource,'/ritm_payload')