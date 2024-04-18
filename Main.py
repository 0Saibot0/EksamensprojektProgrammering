from flask import Flask, render_template, redirect, session
from flask_session import Session
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
app.config["SESSION_PERMANENT"] = False
app.config["SECRET_TYPE"] = "filesystem"


@app.route('/', methods=["POST", "GET"]) #
def home():
    if not session.get("name"):
        return redirect("/login")
    
    return render_template('home.html', title='HOME')

@app.route('/login/', methods=["POST", "GET"])
def login():
    form = loginForm()

    return render_template('login.html', title='login')

@app.route('/login/', methods=["POST", "GET"])
def register():
    return render_template('register.html', title='register')


# Runs app
if __name__ == '__main__':
    app.run(debug=True)