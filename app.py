from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import wikipedia
def get_wikipedia_summary(search_term):
    try:
        result = wikipedia.summary(search_term, sentences=8)
        return result
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Ambiguous search term. Please specify: {', '.join(e.options)}"
    except wikipedia.exceptions.PageError:
        return "No information."


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medical_data.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Define User and MedicalData models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    medical_data = db.relationship('MedicalData', backref='user', lazy=True)

class MedicalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    blood_type = db.Column(db.String(5))
    allergies = db.Column(db.Text)

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(first_name=first_name, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    search_summary = None  # Initialize the search summary as None
    
    if request.method == 'POST':
        search_term = request.form['search_term']
        search_summary = get_wikipedia_summary(search_term)
        print(search_term)
    
    return render_template('dashboard.html', search_summary=search_summary)


@app.route('/edit-medical-data', methods=['GET', 'POST'])
@login_required
def edit_medical_data():
    if request.method == 'POST':
        current_user.medical_data.name = request.form['name']
        current_user.medical_data.age = request.form['age']
        current_user.medical_data.blood_type = request.form['blood_type']
        current_user.medical_data.allergies = request.form['allergies']
        db.session.commit()
        flash('Medical data updated successfully', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_medical_data.html')

@app.route('/add-medical-data', methods=['GET', 'POST'])
@login_required
def add_medical_data():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        blood_type = request.form['blood_type']
        allergies = request.form['allergies']
        
        # Create a new MedicalData instance
        new_medical_data = MedicalData(
            user_id=current_user.id,
            name=name,
            age=age,
            blood_type=blood_type,
            allergies=allergies
        )
        
        db.session.add(new_medical_data)
        db.session.commit()
        
        flash('Medical data added successfully', 'success')
        
        return redirect(url_for('dashboard'))
    
    return render_template('add_medical_data.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

