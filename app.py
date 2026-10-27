import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

# A secret key is required by Flask to protect user login sessions
app.secret_key = 'super_secret_cloud_vault_key_123'

STORAGE_FOLDER = 'cloud_storage'

# Define our secure master password
MASTER_PASSWORD = "password123"

def get_backed_up_files():
    if not os.path.exists(STORAGE_FOLDER):
        os.makedirs(STORAGE_FOLDER)
        
    file_list = []
    for filename in os.listdir(STORAGE_FOLDER):
        filepath = os.path.join(STORAGE_FOLDER, filename)
        if os.path.isfile(filepath):
            timestamp = os.path.getmtime(filepath)
            readable_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            file_list.append({
                'name': filename,
                'time': readable_time,
                'status': 'Backed Up Successfully ✅'
            })
    return file_list

# --- Authentication Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        # Accepts any username, as long as the password is password123
        if password == MASTER_PASSWORD and username != "":
            session['logged_in'] = True
            session['username'] = username  # Remember the user's name!
            return redirect(url_for('home'))
        else:
            error = 'Invalid Security Protocol Credentials. Access Denied.'
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# --- Main App Routes ---

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    tracked_files = get_backed_up_files()
    # Send both the files and the logged-in username to the HTML template
    return render_template('index.html', files=tracked_files, current_user=session.get('username'))

@app.route('/upload', methods=['POST'])
def upload():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    uploaded_file = request.files['my_file']
    if uploaded_file.filename != '':
        destination_path = os.path.join(STORAGE_FOLDER, uploaded_file.filename)
        uploaded_file.save(destination_path)
        
    return redirect(url_for('home'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    filepath = os.path.join(STORAGE_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
