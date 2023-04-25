from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, IntegerField, PasswordField, TextAreaField, SelectField
from wtforms.validators import InputRequired, EqualTo, Length
#from wtforms.fields.html5 import IntegerRangeField
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


from PIL import Image
import uuid
import os
import imghdr
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = "UIoiwehHEF02394HIG834098ioa43shd34lk"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///FarmersDB"

#app.config['UPLOAD_PATH'] = 'static'
#app.config['MAX_CONTENT_LENGTH'] = 1024*1024*5
#app.config['UPLOAD_EXTENSIONS'] = ['.jpg','.png','.gif','.jpeg']



db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view= "farmerSignIn"
login_manager.login_message_category= "Please sign in to view this page"

admin = Admin(app)



upload_path = os.path.join(app.root_path, 'static')
print(upload_path)



##VALIDATING IMAGE EXTENSION
def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.'+(format if format != 'jpeg' else 'jpg')





#FARMER LOADER: LOADS FARMER ID FOR SESSION PURPOSE
@login_manager.user_loader
def load_farmer(farmer_id):
    return Farmers.query.get(int(farmer_id))


#THE DATABASE TABLE MODELS
class Farmers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.Text)
    phone_number = db.Column(db.Integer)
    email = db.Column(db.Text)
    password = db.Column(db.Text)
    crops = db.relationship("Crops", backref="farmers", lazy=True)
    blogs = db.relationship("Blogs", backref="farmers", lazy= True)

    def __init__(self, username, phone_number, email, password):
        self.phone_number = phone_number
        self.username = username;
        self.email = email
        self.password = password

class Crops(db.Model):
    crops_id = db.Column(db.Integer, primary_key = True)
    crop_name = db.Column(db.String(20))
    crop_description = db.Column(db.Text)
    crop_quantity = db.Column(db.Integer)
    crop_price = db.Column(db.Integer)
    crop_picLoc = db.Column(db.Text)
    availability = db.Column(db.String)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable = False)

    def __init__(self,crop_name , crop_description, crop_quantity,availability, crop_price, crop_picLoc, farmer_id):
        self.crop_name = crop_name
        self.crop_description = crop_description;
        self.crop_quantity = crop_quantity
        self.crop_price = crop_price
        self.crop_picLoc = crop_picLoc
        self.availability=availability
        self.farmer_id = farmer_id



class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(20))
    comment = db.Column(db.Text)
    date_posted = db.Column(db.DateTime)
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.blog_id'), nullable=False)
    def __init__(self, name, blog_id ,comment, date_posted):
        self.name = name
        self.comment = comment
        self.blog_id =blog_id
        self.date_posted =date_posted


class Blogs(db.Model):
    blog_id = db.Column(db.Integer, primary_key= True)
    title = db.Column(db.String(50))
    sub_title = db.Column(db.String(50))
    author = db.Column(db.String(10))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime)
    pic_loc= db.Column(db.Text)
    comments = db.relationship("Comments", backref="comments", lazy= True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)

    def __init__(self, title, sub_title, content, author, date_posted, pic_loc, farmer_id):
        self.title = title
        self.sub_title = sub_title
        self.author = author
        self.content = content
        self.author = author
        self.date_posted = date_posted
        self.pic_loc = pic_loc
        self.farmer_id = farmer_id


class Orders(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    email = db.Column(db.Text)
    phone_number = db.Column(db.Integer)
    country = db.Column(db.Text)
    city = db.Column(db.Text)
    date_posted = db.Column(db.DateTime)
    quantity = db.Column(db.Integer)
    address = db.Column(db.Text)
    crop_id = db.Column(db.Integer)
    farmer_id = db.Column(db.Integer)

    def __init__(self, first_name, last_name, email, date_posted,quantity, phone_number, country,city,address,crop_id,farmer_id ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.country = country
        self.city = city
        self.address = address
        self.date_posted = date_posted
        self.quantity =quantity
        self.crop_id = crop_id
        self.farmer_id =farmer_id

#END DATABASE TABLE MODEL


#adding model views to admin

admin.add_view(ModelView(Farmers, db.session))
admin.add_view(ModelView(Comments, db.session))
admin.add_view(ModelView(Blogs, db.session))
admin.add_view(ModelView(Orders, db.session))



#WTFORMS FOR LOGIN REGISTER POST BLOGS ...
class farmerRegisterForm(FlaskForm):
    username = StringField("username" , validators=[InputRequired()])
    phone_number = IntegerField("phone_number", validators=[InputRequired()])
    email = StringField("email", validators=[InputRequired()])
    password = PasswordField("password", validators=[InputRequired(), EqualTo("confirm_pass", message= "Passwords Don't Match")])
    confirm_pass = PasswordField("confirm_pass")

class farmerSignInForm(FlaskForm):
    username = StringField("username" , validators=[InputRequired()])
    password = PasswordField("password", validators=[InputRequired()])

class farmerCropForm(FlaskForm):
    crop_name  = StringField("crop_name", validators=[InputRequired()])
    crop_description = StringField("crop_description", validators=[InputRequired()])
    crop_quantity = IntegerField("crop_quantity", validators=[InputRequired()])
    crop_price = IntegerField("crop_price", validators=[InputRequired()])
    availability = SelectField("Is crop Available?", choices=[('yes', 'TRUE'), ('no', 'FALSE')])
    photo = FileField(validators=[FileRequired()])


class blogForm(FlaskForm):
        title  = StringField("title", validators=[InputRequired()])
        sub_title = StringField("sub_title", validators=[InputRequired()])
        content = TextAreaField("content", validators=[InputRequired()])
        photo = FileField(validators=[FileRequired()])


class purchaseForm(FlaskForm):
    first_name = StringField("first_name", validators=[InputRequired()])
    last_name = StringField("last_name", validators=[InputRequired()])
    email = StringField("email", validators=[InputRequired()])
    phone_number = IntegerField("phone_number", validators=[InputRequired()])
    Quantity = IntegerField('Quantity', validators=[InputRequired()] )
    country = StringField('country', validators=[InputRequired()])
    city = StringField('city', validators=[InputRequired()])
    address = StringField("address", validators=[InputRequired()])

class commentForm(FlaskForm):
    name = StringField("name", validators=[InputRequired()])
    comment= StringField('comment', validators=[InputRequired()])

#END INPUT FORM




#ROUTES

@app.route("/")
def index():
    crops = Crops.query.all()
    return render_template("index.html", crops =crops )

@app.route("/market/")
def market():
    form = purchaseForm()
    crops = Crops.query.all()
    return render_template("market.html" , crops =crops, form =form )

@app.route('/view/<int:crop_id>/<int:farmerId>')
def view(crop_id, farmerId):
    crop = Crops.query.get(crop_id)
    otherCrops = Crops.query.filter_by(farmer_id=farmerId)
    form = purchaseForm()
    return render_template("view.html", crop=crop,  form = form, otherCrops = otherCrops)


@app.route("/purchase/<int:crop_id>/<int:farmer_id>", methods=["GET", "POST"])
def purchase(crop_id, farmer_id):
    form = purchaseForm()

    if request.method=="POST" and form.validate_on_submit():
        new_order = Orders(first_name=form.first_name.data, last_name=form.last_name.data,
        email =form.email.data, phone_number=form.phone_number.data, country=form.country.data,
        city=form.city.data,address=form.address.data,date_posted= datetime.now(), quantity =form.Quantity.data,
        crop_id=crop_id, farmer_id=farmer_id )
        db.session.add(new_order)
        db.session.commit()
        flash("YOUR ORDER HAS BEEN MADE")
        return redirect(url_for('market'))
    return redirect(url_for('market'))


@app.route("/farmerSignIn/", methods=["GET", "POST"])
def farmerSignIn():
    form = farmerSignInForm()
    if request.method == "POST" and form.validate():
        farmer = Farmers.query.filter_by(username = form.username.data).first()
        if farmer:
            if check_password_hash(farmer.password, form.password.data):
                login_user(farmer)
                return redirect(url_for('farmerDashBoard'))
        flash("incorrect credentials")
    return render_template("farmerTemps/farmerSignIn.html", form=form)

@app.route("/farmerRegister/", methods=["GET" , "POST"])
def farmerRegister():
    form = farmerRegisterForm()

    if request.method == "POST" and form.validate():
        farmer = Farmers.query.filter_by(username = form.username.data).first()
        if farmer:
            flash("Username Already Exist Please Choose Another One")
            return redirect(url_for('farmerRegister'))
        else:
            pass_hash = generate_password_hash(form.password.data, method="sha256")
            new_farmer = Farmers(username = form.username.data, phone_number = form.phone_number.data,
                    email = form.email.data, password = pass_hash)
            db.session.add(new_farmer)
            db.session.commit()
            new_dir = 'uploads/'+str(form.username.data)
            try:
                path = os.path.join(upload_path, new_dir)
                os.mkdir(path)
                blog_path = os.path.join(path, 'blogPic')
                os.mkdir(blog_path)
            except OSError as error:
                print(error)
            return redirect(url_for('farmerSignIn'))
    return render_template("farmerTemps/farmerRegister.html", form =form)

@app.route("/farmerDashBoard/")
@login_required
def farmerDashBoard():
    form = farmerCropForm()
    blogform = blogForm()
    crops = Crops.query.filter_by(farmer_id=current_user.id).all()
    orders = Orders.query.filter_by(crop_id=current_user.id).all()
    ordercount = Orders.query.filter_by(farmer_id=current_user.id).count()
    cropCount = Crops.query.filter_by(farmer_id=current_user.id).count()
    personal_blogsCount = Blogs.query.filter_by(farmer_id = current_user.id).count()

    return render_template("farmerTemps/farmerDashBoard.html",form=form, blogform=blogform, crops =crops, orders=orders, ordercount = ordercount, cropCount = cropCount, personal_blogsCount =personal_blogsCount)

@app.route("/editCrop/<int:crop_id>/", methods=["GET", "POST", "PATCH"])
@login_required
def edit_crop(crop_id):
    form = farmerCropForm()
    crop = Crops.query.get(crop_id)
    if request.method == "POST":
        crop.crop_name = form.crop_name.data
        crop.crop_description = form.crop_description.data
        crop.crop_quantity = form.crop_quantity.data
        crop.crop_price = form.crop_price.data
        crop.availability = form.availability.data
        db.session.add(crop)
        db.session.commit()
        flash("Crop Record Updated")
        return redirect(url_for('farmerMarket'))
    return render_template("farmerTemps/editCrop.html", crop =crop)

@app.route("/editblog/<int:Blogid>/", methods=["GET", "POST", "PATCH"])
@login_required
def edit_blog(Blogid):
    form = blogForm()
    blog = Blogs.query.get(Blogid)
    if request.method == "POST":
        blog.title = form.title.data
        blog.sub_title = form.sub_title.data
        blog.content = form.content.data

        db.session.add(blog)
        db.session.commit()
        flash("Blog Updated")
        return redirect(url_for('blogsite'))
    return render_template("farmerTemps/blogEdit.html", blog =blog)








@app.route("/deleteRecord/<int:id>/", methods=["DELETE", "PATCH", "GET"])
def deleteRecord(id):
    Crops.query.filter_by(crops_id=id).delete()
    db.session.commit()
    flash("crop deleted successfully")
    return redirect(url_for('farmerMarket'))



@app.route("/farmerMarket/")
@login_required
def farmerMarket():
    form = farmerCropForm()
    crops = Crops.query.filter_by(farmer_id=current_user.id).all()
    allCrops = Crops.query.all()

    return render_template("farmerTemps/farmerMarket.html",allCrops=allCrops, crops =crops, form=form)


@app.route("/orders/")
@login_required
def orders():
    orders = Orders.query.filter_by(farmer_id=current_user.id).all()
    return render_template("farmerTemps/farmerOrder.html", orders= orders)

@app.route("/vieworders/<int:orderId>/<int:crop_id>/")
@login_required
def vieworders(crop_id, orderId):
    crop = Crops.query.get(crop_id)
    order = Orders.query.get(orderId)
    return render_template("farmerTemps/viewOrder.html",order =order, crop= crop)






@app.route("/farmerPostCrop/", methods=["GET", "POST"])
def farmerPostCrop():
    form = farmerCropForm()
    location = current_user.username
    if request.method == "POST" and form.validate_on_submit():
        f = form.photo.data
        image_id = str(uuid.uuid4())
        file_name = image_id + ".png"
        file_path = os.path.join(upload_path+'/uploads/'+location, file_name)
        Image.open(f).save(file_path)
        original_file_path= upload_path+'/uploads/'+location
        #_image_resize(original_file_path, image_id, 600, 'lg')
        #_image_resize(original_file_path, image_id, 300, 'sm')
        new_path = os.path.join('uploads/'+location+'/'+ file_name)

        new_crop = Crops(crop_name = form.crop_name.data, crop_description = form.crop_description.data, crop_quantity = form.crop_quantity.data,
                    crop_price = form.crop_price.data, crop_picLoc =new_path, farmer_id = current_user.get_id(), availability=form.availability.data )
        db.session.add(new_crop)
        db.session.commit()
        flash("Crop posted successfully")
        return redirect(url_for('farmerDashBoard'))
    return render_template("farmerTemps/farmerPostCrop.html", form=form)






@app.route("/blogsite/")
def blogsite():
    if(not current_user.is_authenticated):
        blogs = Blogs.query.order_by(Blogs.date_posted.desc()).all()
        personal_blogs = blogs
    else:
        personal_blogs = Blogs.query.filter_by(farmer_id = current_user.id)
        blogs = Blogs.query.order_by(Blogs.date_posted.desc()).all()
    return render_template("blogsite.html", personal_blogs=personal_blogs, blogs= blogs)


@app.route("/read/<int:blog_id>/", methods=["GET", "POST"])
def readBlog(blog_id):
    form = commentForm()
    blog = Blogs.query.get(blog_id)
    farmer = Farmers.query.get(blog.farmer_id)
    allBlogs = Blogs.query.filter_by(farmer_id=blog.farmer_id).all()
    comments = Comments.query.filter_by(blog_id = blog_id).all()
    return render_template("blogRead.html",allBlogs=allBlogs, farmer=farmer ,blog_id =blog_id, comments =comments, blog=blog, form =form)



@app.route("/addComment/<int:blog_id>", methods=["GET", "POST"])
def addComment(blog_id):
    form = commentForm()
    if request.method =="POST" and form.validate_on_submit():
        new_comment = Comments(name = form.name.data, date_posted=datetime.now(), comment=form.comment.data, blog_id= blog_id)
        db.session.add(new_comment)
        db.session.commit()
        flash("Commented")
        redirect(url_for('readBlog', blog_id = blog_id, form = commentForm()))
    else:
        flash("Commented unsuccessful")
    return redirect(url_for('readBlog', blog_id = blog_id, form = commentForm()))

@app.route("/Blog/<int:farmer_id>/Create/", methods=["GET", "POST"])
@login_required
def createBlog(farmer_id):
    form = blogForm()
    #blogPicLoc = current_user.username
    if request.method == "POST" and form.validate_on_submit():
        f = form.photo.data
        location = current_user.username+'/blogPic/'
        image_id = str(uuid.uuid4())
        file_name = image_id + ".png"
        file_path = os.path.join(upload_path+'/uploads/'+location, file_name)
        Image.open(f).save(file_path)
        db_pic_path = 'uploads/'+location+file_name

        new_blog = Blogs(title = form.title.data, sub_title =form.sub_title.data, content =form.content.data,
            author=current_user.username, date_posted=datetime.now(), pic_loc = db_pic_path, farmer_id = current_user.get_id())
        db.session.add(new_blog)
        db.session.commit()
        flash("Blog Posted successfully")
        return redirect(url_for('blogsite'))

    return render_template("farmerTemps/blogCreate.html", form = form)





@app.route("/farmerProfile/")
@login_required
def farmerProfile():
    farmer = Farmers.query.get(current_user.id)
    allFarmers = Farmers.query.all()
    return render_template("farmerTemps/farmerProfile.html", farmer =farmer, allFarmers=allFarmers)



@app.route("/editNum/<int:id>", methods=["GET", "POST"])
@login_required
def EditNUm(id):
    farmer= Farmers.query.get(id)
    if request.method =="POST":

        farmer.phone_number = request.form['phone']
        db.session.add(farmer)
        db.session.commit()
        flash("Changed successfully")
        redirect(url_for('farmerProfile'))
    return redirect(url_for('farmerProfile'))


@app.route("/editEmail/<int:id>", methods=["GET", "POST"])
@login_required
def editEmail(id):
    farmer= Farmers.query.get(id)
    if request.method =="POST":

        farmer.email = request.form['email']
        db.session.add(farmer)
        db.session.commit()
        flash("Changed successfully")
        redirect(url_for('farmerProfile'))
    return redirect(url_for('farmerProfile'))








@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



################################
    #Resize Image Function#
################################

def _image_resize(orginial_file_path, image_id, image_base, extension):
    file_path = os.path.join(orginial_file_path, image_id+".png")
    new_path= orginial_file_path + '/resized'
    print(new_path)
    image = Image.open(file_path)
    wpercent = (image_base/ float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    image = image.resize((image_base, hsize), Image.ANTIALIAS)
    modified_file_path = os.path.join(new_path,image_id +'.'+extension+'.png')
    image.save(modified_file_path)
    return

if __name__ == "__main__":
    app.run(debug=True, port = 5000)
