from flask import Flask, render_template, redirect, session, flash, request, jsonify
import sqlite3
import math
from datetime import datetime
from flask_session import Session
from sqlalchemy.orm import create_session
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from Forms import LoginForm, RegisterForm
from dbhelper import Users, engine
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg19 import preprocess_input
import os
from PIL import Image
import io

app = Flask(__name__)
app.config.from_object(Config)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Load the model globally so it can be used in the prediction function
model_path = 'model/vgg19_final_model.keras'

try:
    model = load_model(model_path)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Define labels
labels = {0: 'Melanoma', 1: 'Nevus', 2: 'Seborrheic Keratosis'}

def load_and_prepare_image(image_file) -> np.ndarray:
    """
    Loads and preprocesses an image for VGG19 model prediction.

    Parameters:
    - image_file (FileStorage): Image file object from Flask request.

    Returns:
    - np.ndarray: Preprocessed image ready for model input.
    """
    img = Image.open(image_file.stream)  # Open the image file stream
    img = img.resize((224, 224))  # Resize the image to 224x224 pixels
    img_array = image.img_to_array(img)
    img_array_expanded = np.expand_dims(img_array, axis=0)



    return preprocess_input(img_array_expanded)

@app.route('/', methods=["POST", "GET"])
def home():
    if not session.get("name"):
        return redirect("/login")
    conn = sqlite3.connect("static/db/Bruger.db")
    cursor = conn.cursor()
    cursor.execute("SELECT result FROM results")
    result = cursor.fetchone()[0]
    cursor.execute("SELECT accuracy FROM results")
    accuracy = cursor.fetchone()[0]
    conn.close()
    return render_template('home.html', result=result, accuracy=accuracy, title='HOME')

@app.route('/login/', methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_session = create_session(autocommit=False, autoflush=False, bind=engine)
        user = user_session.query(Users).filter_by(Username=form.username.data).first()
        if user and check_password_hash(user.Password, form.password.data):
            user_session.close()
            session["name"] = form.username.data
            return redirect('/')
        else:
            flash("Entered password is wrong")
    return render_template("login.html", form=form, title='The Interrogator')

@app.route('/register/', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    user_session = create_session(autocommit=False, autoflush=False, bind=engine)
    if form.validate_on_submit():
        user = user_session.query(Users).filter_by(Username=form.username.data).first()
        if user:
            return redirect('/login/')
        new_user = Users(
            Username=form.username.data, 
            Mail=form.mail.data, 
            Password=generate_password_hash(form.password.data, method='pbkdf2:sha256')
        )
        user_session.add(new_user)
        user_session.commit()
        if new_user:
            user_session.close()
            return redirect('/login/')
    return render_template('register.html', form=form, title='register')

@app.route('/upload/', methods=["POST", "GET"])
def upload():
    if request.method == "POST":
        print("HERE")
        if 'imageInput' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['imageInput']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        try:
            prepared_image = load_and_prepare_image(file)
            predictions = model.predict(prepared_image)
            predicted_class_indices = np.argmax(predictions, axis=1)
            confidence = predictions[0][predicted_class_indices[0]] * 100
            predicted_label = labels.get(predicted_class_indices[0], "Unknown")
            result = f"The uploaded mole is predicted to be {predicted_label} with a confidence of {confidence:.2f}%."
            
            # Print statement to check if it passed through the model



            conn = sqlite3.connect("static/db/Bruger.db")
            cursor = conn.cursor()

            cursor.execute("""INSERT INTO results (User, result, date, accuracy) VALUES (?, ?, ?, ?)""", (session["name"], predicted_label, datetime.now().strftime("%d/%m - %Y"), math.floor(confidence)))

            conn.commit()
            conn.close()



            print(f"Prediction made: {predicted_label} with confidence {confidence:.2f}%")
            
            redirect("/")

            return render_template('upload.html', title='Upload', result=result)
        except Exception as e:
            flash(f'Error processing file: {e}')
            return redirect(request.url)
    return render_template('upload.html', title='upload')



@app.route('/list/', methods=["POST", "GET"])
def list():
    conn = sqlite3.connect("static/db/Bruger.db")
    cursor = conn.cursor()
    
    # Fetch rows where User matches the session name
    cursor.execute("SELECT result, date, accuracy FROM results WHERE User = ? ORDER BY ID DESC", (session["name"],))
    results = cursor.fetchall()
    conn.close()
    
    return render_template('list.html', title="List", results=results)


@app.route('/help/', methods=["POST", "GET"])
def help():
    return render_template('help.html', title='help')

@app.route('/settings/', methods=["POST", "GET"])
def settings():
    return render_template('settings.html', title='settings')

@app.route("/logout/")
def logout():
    session["name"] = None
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)


