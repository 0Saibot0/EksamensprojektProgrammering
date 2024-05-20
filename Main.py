from flask import Flask, render_template, redirect, session, flash, request
from flask_session import Session
from sqlalchemy.orm import create_session
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from Forms import LoginForm, RegisterForm
from dbhelper import Users, engine
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg19 import preprocess_input
from tensorflow.keras.models import load_model

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



@app.route('/register/', methods=["POST", "GET"])
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
            Password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
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
        uploaded_file = request.files['imageInput']
        # Now you have access to the uploaded file. You can save it, process it, etc.
        # For example, to save it to a specific directory:

        model_path = 'model/vgg19_model.json'
        image_path = uploaded_file

        predicted_label, confidence = predict_mole(image_path, model_path)
        print(f"The uploaded mole is predicted to be {predicted_label} with a confidence of {confidence * 100:.2f}%.")
        
    return render_template('upload.html', title='upload')

@app.route('/list/', methods=["POST", "GET"])
def list():
    return render_template('list.html', title='list')

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

def load_and_prepare_image(image_path, target_size):
    img = image.load_img(image_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array_expanded = np.expand_dims(img_array, axis=0)
    return preprocess_input(img_array_expanded)  # Preprocess for VGG19

def predict_mole(image_path, model_path):
    # Load the VGG19 model
    model = load_model(model_path)
    
    # Prepare the image
    prepared_image = load_and_prepare_image(image_path, target_size=(224, 224))
    
    # Make prediction
    predictions = model.predict(prepared_image)
    predicted_class_index = np.argmax(predictions, axis=1)[0]  # Get the index of the max prediction score
    prediction_probability = predictions[0][predicted_class_index]  # Probability of the predicted class
    
    # Assuming class indices are {0: 'malignant', 1: 'benign', 2: 'Benign'}
    labels = {0: 'Melanoma', 1: 'Nevus', 2: 'Seborrheic Keratosis'}  
    predicted_label = labels[predicted_class_index]
    
    return predicted_label, prediction_probability
# Runs app
if __name__ == '__main__':
    app.run(debug=True)