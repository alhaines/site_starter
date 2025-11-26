from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# The DB will be set by init_auth
db = None

def init_auth(app, database):
    """Initialize the auth blueprint with the app and database.

    Call this from the application (e.g. in app.py) after creating the DB
    instance: init_auth(app, db)
    """
    global db
    db = database
    app.register_blueprint(auth_bp)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You must be logged in to view this page.", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    global db
    # If the user is already logged in and this is a GET, immediately redirect to menu
    if request.method == 'GET' and (session.get('IFLOGED_IN') or session.get('user_id')):
        # Assuming 'menu.show_menu' is the function name for your menu page
        return redirect(url_for('menu.show_menu'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Fetch user data, including 'level'
        user_data = db.get_data("SELECT id, username, password_hash, level FROM users WHERE username = %s", (username,))
        
        # --- SUCCESSFUL LOGIN BLOCK ---
        if user_data and check_password_hash(user_data[0]['password_hash'], password):
            session['user_id'] = user_data[0]['id']
            session['username'] = user_data[0]['username']
            session['IFLOGED_IN'] = True  # Set legacy flag for backward compatibility
            # normalize stored level to int when possible
            try:
                session['level'] = int(user_data[0].get('level') if isinstance(user_data[0], dict) else user_data[0][3])
            except Exception:
                # fallback: treat as level 1
                session['level'] = 1
            flash(f"Welcome back, {session['username']}!", "success")
            
            # Redirect to menu after successful login
            return redirect("https://login.your_domain/menu")
            
        else:
            flash("Invalid username or password.", "error")
            return render_template('login.html')
            
    # Handles the initial GET request for the login page
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    global db
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zipcode')
        birthday = request.form.get('birthday')
        email = request.form.get('email')
        phone1 = request.form.get('phone1')
        phone2 = request.form.get('phone2')
        comment = request.form.get('comment')
        # Accept the hidden 'level' field from the registration form, default to 1
        try:
            level = int(request.form.get('level', 1))
        except Exception:
            level = 1
        
        if db.get_data("SELECT id FROM users WHERE username = %s", (username,)):
            flash("That username is already taken.", "error")
            return render_template('register.html')
            
        password_hash = generate_password_hash(password)
        query = """
            INSERT INTO users (username, password_hash, firstname, lastname, address, city, state,
                               zipcode, birthday, email, phone1, phone2, comment,level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (username, password_hash, firstname, lastname, address, city, state,
                  zipcode, birthday, email, phone1, phone2, comment,level)
        db.put_data(query, params)
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.login'))
