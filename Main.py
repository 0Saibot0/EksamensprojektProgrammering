from flask import Flask, render_template, redirect, session, flash
from flask_session import Session
from sqlalchemy.orm import create_session
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from Forms import LoginForm, RegisterForm
from dbhelper import Users, engine

app = Flask(__name__)
app.config.from_object(Config)
app.config["SESSION_PERMANENT"] = False
app.config["SECRET_TYPE"] = "filesystem"
Session(app)

@app.route('/', methods=["POST", "GET"])
def home():
    if not session.get("name"):
        return redirect("/login")
    
    return render_template('home.html', title='HOME')





@app.route('/login/', methods=["POST", "GET"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user_session = create_session(autocommit=False, autoflush=False, bind=engine)
        user =user_session.query(Users).filter_by(Username=form.username.data).first()

        if user:
            if check_password_hash(user.Password, form.password.data):
                user_session.close()
                session["name"] = form.username.data
                return redirect('/')
            else:
                flash("Entered password is wrong")

    return render_template("login.html", form=form, title='The Interrogator')

@app.route('/login/', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    user_session = create_session(autocommit=False, autoflush=False, bind=engine)
    
    if form.validate_on_submit():
        print("Registation request recieved")
        user = user_session.query(Users).filter_by(Username=form.username.data).first()
        
        if user:
            return redirect('/login/')
        
        new_user = Users(
            Username = form.username.data, 
            Mail = form.mail.data, 
            Password = generate_password_hash(form.password.data, method='sha256')
        )
        user_session.add(new_user)
        user_session.commit()
        
        if new_user:
            user_session.close()
            return redirect('/login/')
    
    return render_template('register.html', title='register')


# Runs app
if __name__ == '__main__':
    app.run(debug=True)