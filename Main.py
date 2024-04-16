from flask import Flask, render_template, redirect, session
from flask_session import Session
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
app.config["SESSION_PERMANENT"] = False
app.config["SECRET_TYPE"] = "filesystem"
Session(app)


@app.route('/', methods=["POST", "GET"])
def home():

    return render_template('home.html', title='HOME')




# Runs app
if __name__ == '__main__':
    app.run(debug=True)