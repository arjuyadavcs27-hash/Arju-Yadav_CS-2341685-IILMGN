import hashlib
import os
from flask import Flask, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

def verify_admin_credentials(username, password):
    # Check if admin credentials file exists
    if not os.path.exists("data/admin_credentials.txt"):
        return False
    
    # Read admin credentials
    with open("data/admin_credentials.txt", "r") as f:
        lines = f.readlines()
        stored_username = lines[0].split(": ")[1].strip()
        stored_password_hash = lines[1].split(": ")[1].strip()
    
    # Hash the provided password
    provided_password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Verify credentials
    return username == stored_username and provided_password_hash == stored_password_hash

@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('email')
    password = request.form.get('password')
    
    if verify_admin_credentials(username, password):
        session['admin_logged_in'] = True
        session['admin_username'] = username
        flash('Login successful!', 'success')
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid credentials. Please try again.', 'error')
        return redirect(url_for('admin_login_page'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login_page'))

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('admin_login_page'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

if __name__ == '__main__':
    app.run(debug=True) 