from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12345@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'SuperSecurePassword'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), unique=True)
    password = db.Column(db.String(32))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.username = password


# @app.route("/signup")
# def display_signup():
#     return render_template('signup.html')


@app.route("/signup", methods=['POST', 'GET'])
def signup_validate():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        re_enter = request.form['re-enter']

        username_error = ''
        password_error = ''
        password_mismatch = ''
        empty_field_error = ''
        duplicate_username_error = ''

        if username == '' or password == '' or re_enter == '':
            empty_field_error = "One or more fields are invalid"
            password = ''
            re_enter = ''

        elif len(password) < 3:
            password_error = 'Password must be greater than 3 characters'
            password = ''
            re_enter = ''

        elif password != re_enter:
            password_mismatch = "Passwords don't match"
            password = ''
            re_enter = ''   

        elif len(username) < 3:
            username_error = "Username must be greater than 3 characters"
            username = ''
            password = ''
            re_enter = ''

        existing_user = User.query.filter_by(username=username).first()
        
        ######## TODO - check to make sure following if statement works!

        if existing_user:
            duplicate_username_error = 'Username already exists'
            username = ''
            password = ''
            re_enter = ''


        if (not username_error and 
            not password_error and
            not password_mismatch and
            not empty_field_error and
            not duplicate_username_error
            ):

            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

        else:
            return render_template(
                'signup.html',
                username_error=username_error,
                password_error=password_error, 
                mismatch_error=password_mismatch,
                empty_field_error=empty_field_error,
                duplicate_username_error=duplicate_username_error,
                username=username, 
                password=password,
                password_match=re_enter
                )        
    
    return render_template('signup.html')   

@app.route('/login', methods=['POST', 'GET'])
def login_validate():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] 
       
        user = User.query.filter_by(username=username).first()
       
        if user and user.password == password:
            session['username'] = username
            flash('logged in')
            return redirect('/newpost')

        elif user and user.password != password:
            flash("Password is incorrect")

        elif not user:
            flash('Username does not exist')

    return render_template('login.html')

@app.route('/blog', methods=['POST', 'GET'])
def index():
    
    blog_id = request.args.get('id')

    if blog_id == None:
        blogs = Blog.query.all()

        return render_template('/blogs.html', blogs=blogs)
        
    else:
        blog_id_int= int(blog_id)
        blog = Blog.query.get(blog_id_int)

        return render_template('/blogdisplay.html',
            blog=blog)    
    

@app.route('/newpost')
def display_add_blog():
   
    return render_template('addblog.html')

    
@app.route('/newpost', methods=['POST'])
def add_blog():

    owner = User.query.filter_by(username=session['username']).first()

    title = request.form['title']
    body = request.form['body']
    title_error = ''
    body_error = ''

    if title == '':
        title_error = "Please fill in the title"
        

    if body == '':
        body_error = "Please fill in the body"
    

    if title_error or body_error:
        return render_template('addblog.html',
            title_error = title_error,
            body_error = body_error,
            title = title,
            body = body)

    else:
        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()      
        
        new_blog_id = new_blog.id

        return redirect("/blog?id={0}".format(new_blog_id))



if __name__ == '__main__':
    app.run()