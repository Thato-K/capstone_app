from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, jsonify, current_app
import sqlite3
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
import os
from werkzeug.utils import secure_filename
import json


app_rf = Blueprint("app_rf", __name__, template_folder="rf_templates")

def init_app(app):
    UPLOAD_FOLDER = 'uploads'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.secret_key = 'contamination'

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app_rf.route('/user_upload')
# def user_upload():
#     return render_template('upload.html')

@app_rf.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)

        # Process the uploaded file in chunks
        with open(file_path, 'wb') as f:
            while True:
                chunk = file.read(4096)  # Adjust the chunk size as needed
                if not chunk:
                    break
                f.write(chunk)

        # Process the uploaded file and get the result filename
        result_filename = process_excel_file(filename)

        # Provide the result filename in the response
        return jsonify({'result_filename': result_filename}), 200

    return jsonify({'message': 'Invalid file type'}), 400


@app_rf.route('/download/<result_filename>')
def download_result(result_filename):
    return send_file(os.path.join('uploads', result_filename), as_attachment=True)

@app_rf.route('/process/<filename>', methods=['GET', 'POST'])
def process_uploaded_file(filename):
    # Assuming you have a function to process the Excel data
    result = process_excel_file(filename)

    return render_template('result.html', result=result)

def process_excel_file(filename):
    # Assuming your function reads the Excel file and extracts the necessary data
    df = pd.read_excel(os.path.join('uploads', filename))

    # Drop rows with missing values
    df = df.dropna(subset=['Latitude', 'Longitude', 'Cd_value', 'Cr_value', 'Ni_value', 'Pb_value', 'Zn_value', 'Cu_value', 'Co_value'])

    # Assuming you have functions for data preprocessing and prediction
    results = []
    row_count = 0

    for index, row in df.iterrows():
        if row_count >= 100:
            break
        
        latitude = row['Latitude']
        longitude = row['Longitude']
        cd_value = row['Cd_value']
        cr_value = row['Cr_value']
        ni_value = row['Ni_value']
        pb_value = row['Pb_value']
        zn_value = row['Zn_value']
        cu_value = row['Cu_value']
        co_value = row['Co_value']

        # Create a numpy array with the user input values
        X_new = pd.DataFrame([[latitude, longitude, cd_value, cr_value, ni_value, pb_value, zn_value, cu_value, co_value]],
                             columns=['Latitude', 'Longitude', 'Cd_value', 'Cr_value', 'Ni_value', 'Pb_value', 'Zn_value', 'Cu_value', 'Co_value'])

        # Make a prediction
        y_pred_new = rf_model.predict(X_new)

        # Check if prediction is successful
        if y_pred_new is not None and len(y_pred_new) > 0:
            # Inverse transform the prediction to get the original label
            predicted_label = label_encoder.inverse_transform(y_pred_new)
            predicted_label = predicted_label[0]  # Get the first element of the array

            # Store the data in the results list
            results.append([latitude, longitude, cd_value, cr_value, ni_value, pb_value, zn_value, cu_value, co_value, predicted_label])

            # Store the data in the database
            conn = sqlite3.connect('rf_folder\prediction.db')
            c = conn.cursor()
            c.execute('''INSERT INTO user_data
                         (username, latitude, longitude, cd_value, cr_value, ni_value, pb_value, zn_value, cu_value, co_value, predicted_label)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (session['username'], latitude, longitude, cd_value, cr_value, ni_value, pb_value, zn_value, cu_value, co_value, predicted_label))
            conn.commit()
            conn.close()
            row_count += 1

    # Create a DataFrame from the results list
    result_df = pd.DataFrame(results, columns=['Latitude', 'Longitude', 'Cd_value', 'Cr_value', 'Ni_value', 'Pb_value', 'Zn_value', 'Cu_value', 'Co_value', 'Predicted_Contamination'])

    # Save the DataFrame to an Excel file
    result_filename = f"results_{filename}"
    result_df.to_excel(os.path.join('uploads', result_filename), index=False)

    return result_filename

# Define a route for the login page
@app_rf.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for('app_rf.index'))
    return render_template('login.html')

def username_exists(username):
    conn = sqlite3.connect('rf_folder\prediction.db')
    c = conn.cursor()
    c.execute('SELECT * FROM user_data WHERE username=?', (username,))
    result = c.fetchone()
    conn.close()
    return result is not None

@app_rf.route('/logout')
def logout():
    if 'username' in session:
        clear_user_workspace()
        session.pop('username', None)
    return redirect(url_for('app_rf.login'))

def clear_user_workspace():
    try:
        conn = sqlite3.connect('rf_folder\prediction.db')
        c = conn.cursor()
        c.execute('DELETE FROM user_data')
        conn.commit()
    except Exception as e:
        print(f"Error clearing workspace: {e}")
    finally:
        conn.close()


@app_rf.route('/clear_workspace', methods=['GET', 'POST'])
def clear_workspace():
    if request.method == 'POST':
        clear_user_workspace()  # Call the function to clear the database

        session.pop('username', None)  # Clear the session
        return redirect(url_for('app_rf.login'))

    return render_template('clear_workspace.html')


def check_logged_in():
    return 'username' in session


@app_rf.route('/')
def index():
    if not check_logged_in():
        return redirect(url_for('app_rf.login'))
    username = session.get('username')
    return render_template('index.html', name=username)


@app_rf.route('/contact_us')
def contact_us():
    return render_template('contact.html')

@app_rf.route('/about_us')
def about_us():
    return render_template('about.html')

@app_rf.route('/soil_quality_standards')
def soil_quality_standards():
    return render_template('soil-quality.html')

@app_rf.route('/predictor')
def go_back():
    if not check_logged_in():
        return redirect(url_for('app_rf.login'))
    return render_template('prediction.html')

# Load the model using pickle
with open('rf_folder/rf_model.pkl', 'rb') as model_file:
    rf_model = pickle.load(model_file)

# Load the label encoder
with open('rf_folder/label_encoder.pkl', 'rb') as encoder_file:
    label_encoder = pickle.load(encoder_file)

def has_exceeded_limit(username):
    conn = sqlite3.connect('rf_folder\prediction.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM user_data WHERE username=?', (username,))
    count = c.fetchone()[0]
    conn.close()
    return count >= 150

@app_rf.route('/save_data', methods=['POST'])
def save_data():
    data = request.get_json()

    # Insert the data into the database
    conn = sqlite3.connect('rf_folder\prediction.db')
    c = conn.cursor()
    c.execute('''INSERT INTO user_data
                 (username, latitude, longitude, cd_value, cr_value, ni_value, pb_value, zn_value, cu_value, co_value)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['username'], data['latitude'], data['longitude'], data['cd_value'], data['cr_value'], data['ni_value'],
               data['pb_value'], data['zn_value'], data['cu_value'], data['co_value']))
    conn.commit()
    conn.close()

    # Clear the input fields
    cleared_fields = ['latitude', 'longitude', 'cd_value', 'cr_value', 'ni_value', 'pb_value', 'zn_value', 'cu_value', 'co_value']

    return jsonify({'message': 'Data saved successfully', 'cleared_fields': cleared_fields}), 200


@app_rf.route('/prediction_result', methods=['GET', 'POST'])
def prediction_result():
    if request.method == 'POST':
        conn = sqlite3.connect('rf_folder\prediction.db')
        c = conn.cursor()
        c.execute('SELECT * FROM user_data WHERE username=? ORDER BY id DESC LIMIT 1', (session['username'],))
        result = c.fetchone()
        conn.close()

        if result is not None:
            predicted_label = result[-1]  # Assuming the predicted label is the last column
            latitude = result[2]  # Assuming latitude is the third column
            longitude = result[3]  # Assuming longitude is the fourth column
            return render_template('prediction_result.html', predicted_label=predicted_label, latitude=latitude, longitude=longitude)
        else:
            return render_template('error.html', message="No recent prediction found.")

    return redirect(url_for('app_rf.predict'))

@app_rf.route('/predict', methods=['GET', 'POST'])
def predict():
    latitude = None
    longitude = None

    if request.method == 'POST':
        # Handle the POST request
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        cd_value = request.form.get('cd_value')
        cr_value = request.form.get('cr_value')
        ni_value = request.form.get('ni_value')
        pb_value = request.form.get('pb_value')
        zn_value = request.form.get('zn_value')
        cu_value = request.form.get('cu_value')
        co_value = request.form.get('co_value')
        username = request.form.get('username')

        # Check if any of the input fields are empty
        if any(val is None or val == '' for val in [latitude, longitude, cd_value, cr_value, ni_value, pb_value, zn_value, cu_value, co_value]):
            return render_template('error.html', message="All fields are required.")

        # Convert values to float
        latitude = float(latitude)
        longitude = float(longitude)
        cd_value = float(cd_value)
        cr_value = float(cr_value)
        ni_value = float(ni_value)
        pb_value = float(pb_value)
        zn_value = float(zn_value)
        cu_value = float(cu_value)
        co_value = float(co_value)

        # Create a numpy array with the user input values
        X_new = pd.DataFrame([[latitude, longitude, cd_value, cr_value, ni_value, pb_value, zn_value, cu_value, co_value]],
                             columns=['Latitude', 'Longitude', 'Cd_value', 'Cr_value', 'Ni_value', 'Pb_value', 'Zn_value', 'Cu_value', 'Co_value'])

        # Make a prediction
        y_pred_new = rf_model.predict(X_new)

        # Inverse transform the prediction to get the original label
        predicted_label = label_encoder.inverse_transform(y_pred_new)

        conn = sqlite3.connect('rf_folder\prediction.db')
        c = conn.cursor()
        c.execute('''INSERT INTO user_data
                 (username, latitude, longitude, cd_value, cr_value, ni_value, pb_value, zn_value, cu_value, co_value, predicted_label)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (session.get('username'), latitude, longitude, cd_value, cr_value, ni_value, pb_value, zn_value, cu_value, co_value, predicted_label[0]))
        conn.commit()
        conn.close()

        return render_template('prediction_result.html', predicted_label=predicted_label[0], name=session.get('username'), latitude=latitude, longitude=longitude)

    if has_exceeded_limit(session.get('username', '')):
        return render_template('error.html', message="You have reached the maximum limit of 150 entries.", show_clear_database_button=True)

    # Check for duplicate entry
    if username_exists(session.get('username', ''), latitude, longitude):
        return render_template('error.html', message="You have already submitted an entry with these coordinates.")

    else:
        # Handle the GET request
        if not check_logged_in():
            return redirect(url_for('app_rf.login'))
        return render_template('prediction.html', latitude=latitude, longitude=longitude)


    
# Helper function to check for duplicate entry
def username_exists(username, latitude, longitude):
    conn = sqlite3.connect('rf_folder\prediction.db')
    c = conn.cursor()
    c.execute('SELECT * FROM user_data WHERE username=? AND latitude=? AND longitude=?', (username, latitude, longitude))
    result = c.fetchone()
    conn.close()
    return result is not None

@app_rf.route('/user_data')
def user_data():
    if not check_logged_in():
        return redirect(url_for('app_rf.login'))

    conn = sqlite3.connect('rf_folder\prediction.db')
    c = conn.cursor()
    c.execute('SELECT * FROM user_data WHERE username=?', (session['username'],))
    user_data = c.fetchall()
    conn.close()
    username = request.form.get('username')


    return render_template('user_data.html', user_data=user_data, name=username)

@app_rf.route('/clear_database', methods=['GET', 'POST'])
def clear_database():
    if request.method == 'POST':
        clear_user_workspace()  # Call the function to clear the database

        session.pop('username', None)  # Clear the session
        return redirect(url_for('app_rf.login'))

    # Check if the database is empty
    conn = sqlite3.connect('rf_folder\prediction.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM user_data WHERE username=?', (session['username'],))
    count = c.fetchone()[0]
    conn.close()

    return render_template('clear_database.html', database_empty=count == 0)


def init_db():
    conn = sqlite3.connect('rf_folder\prediction.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  latitude REAL,
                  longitude REAL,
                  cd_value REAL,
                  cr_value REAL,
                  ni_value REAL,
                  pb_value REAL,
                  zn_value REAL,
                  cu_value REAL,
                  co_value REAL,
                  predicted_label TEXT)''')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    app_rf.run(debug=True)
