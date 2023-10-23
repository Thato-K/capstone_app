from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify, send_file, current_app
from models import metal_inputs, input_results, file_data
from create_table import db
from flask_sqlalchemy import SQLAlchemy
import tensorflow as tf
import numpy as np
from werkzeug.utils import secure_filename
import os
from werkzeug.exceptions import RequestEntityTooLarge
import pandas as pd
import csv
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn import metrics
from sqlalchemy import REAL


app_ann = Blueprint("app_ann", __name__, template_folder="ann_templates")


#Decoded classes based on ann_c model
classes = ['very low contamination', 
           'low contamination', 
           'moderate contamination', 
           'high contamination', 
           'very high contamination', 
           'extremely high contamination', 
           'ultra-high contamination']

class_encoder = LabelEncoder()
encoded_classes = class_encoder.fit_transform(classes)
print(encoded_classes)

#Loading ann models
try:
   ann_c = tf.keras.models.load_model("ann_folder/ml_models/ann-c_model.h5")
   ann_r = tf.keras.models.load_model("ann_folder/ml_models/ann-r_model.h5")
   print("Model successfully loaded.")

except Exception as e:
    print(f"Error loading the model: {str(e)}")

@app_ann.route("/home")
def home():
    try:
        if session['username']:
            user = session['username']
            return render_template("index-homepage.html", usr=user)
        else:
            return "User is not logged in!"
    except KeyError:
        return redirect(url_for('app_ann.login'))

@app_ann.route("/login", methods=['POST', 'GET'])
def login():
     if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        if username:
            return render_template("index-homepage.html", name=username)
        else:
             message= "Username required!"
             return render_template("index-login.html", mesg=message)
     else:
          return render_template("index-login.html")
     
@app_ann.route("/logout", methods=['POST', 'GET'])
def logout():
    try:
        if 'username' in session:
            if request.method == 'POST':
                try:
                    input_data = metal_inputs.query.all()
                    for data in input_data:
                        db.session.delete(data)

                    input_data_results = input_results.query.all()
                    for data in input_data_results:
                        db.session.delete(data)

                    file_data_results = file_data.query.all()
                    for data in file_data_results:
                        db.session.delete(data)

                    db.session.commit()  # Commit changes
                    print("Tables cleared successfully")
                except Exception as e:
                    db.session.rollback()  # Rollback changes in case of an error
                    print(f"An error occurred while clearing tables: {str(e)}")
                finally:
                    db.session.close()  # Always close the session

                session.pop('username', None)
                return render_template("index-login.html")
            else:
                return "Tables not cleared"
        else:
            return "User is not logged in!"
    except KeyError:
        return redirect(url_for('app_ann.login'))

    
@app_ann.route("/about_us")
def about_us():
    try:
        if session['username']:
            return render_template("index-about-us.html")
        else:
            return "User not logged in!"
    except KeyError:
        return redirect(url_for('app_ann.login'))

@app_ann.route("/contact_us")
def contact():
    try:
        if session['username']:
            return render_template("index-contact-us.html")
        else: 
            return "User is not logged in!"
    except KeyError:
        return redirect(url_for('app_ann.login'))

@app_ann.route("/gis_map")
def gis_map():
    try:
         if session['username']:
            return render_template("index-Gis-map.html")
         else:
             return "User is not logged in!"
    except KeyError:
        return redirect(url_for('app_ann.login'))

@app_ann.route("/get_contamination_data", methods=['GET'])
def get_contamination_data():
    try:
        if session['username']:
            # Fetch data from both tables
            results_input = input_results.query.all()
            results_file = file_data.query.all()

            # Prepare the data for sending to the frontend
            contamination_data = []

            # Process data from input_results table
            for result in results_input:
                data_entry = {
                    'lat': result.lat,
                    'long': result.long,
                    'cd': result.cd,
                    'cr': result.cr,
                    'ni': result.ni,
                    'pb': result.pb,
                    'zn': result.zn,
                    'cu': result.cu,
                    'co': result.co,
                    'predicted_class': result.predicted_class,
                    'predicted_mCdeg': result.predicted_mCdeg
                }
                contamination_data.append(data_entry)

            # Process data from file_data table
            for result in results_file:
                data_entry = {
                    'lat': result.lat,
                    'long': result.long,
                    'cd': result.cd,
                    'cr': result.cr,
                    'ni': result.ni,
                    'pb': result.pb,
                    'zn': result.zn,
                    'cu': result.cu,
                    'co': result.co,
                    'predicted_class': result.predicted_class,
                    'predicted_mCdeg': result.predicted_mCdeg
                }
                contamination_data.append(data_entry)

            return jsonify(contamination_data)
        else:
            return "User is not logged in!"
    except KeyError:
        return redirect(url_for('app_ann.login'))

@app_ann.route("/standards")
def standards():
    try:
        if session['username']:
            return render_template("index-soil-quality-sta.html")
        else:
             return "User is not logged in!"
    except KeyError:
        return redirect(url_for('app_ann.login'))

method = ''
#INPUT DATA METHOD
@app_ann.route("/input", methods=['POST', 'GET'])
def input():
    if 'username' not in session:
        return redirect(url_for('app_ann.login'))

    try:
        if request.method == 'POST':
            lat = request.form['lat']
            long = request.form['long']
            cd = request.form['cd']
            cr = request.form['cr']
            ni = request.form['ni']
            pb = request.form['pb']
            zn = request.form['zn']
            cu = request.form['cu']
            co = request.form['co']

            hm = metal_inputs(lat, long, cd, cr, ni, pb, zn, cu, co)
            db.session.add(hm)

            try:
                db.session.commit()  # Commit changes
            except Exception as e:
                db.session.rollback()  # Rollback changes in case of an error
                print(f"An error occurred: {str(e)}")

            finally:
                db.session.close()  # Always close the session

            input_status = request.form['input_status']
            session['input_status'] = input_status

            return redirect(url_for("app_ann.process_data"))
        else:
            return render_template("index-soil-prediction.html")
    except Exception as e:
        # Handle any exceptions that may occur during input processing
        return f"An error occurred: {str(e)}"


          
@app_ann.route("/process_data")
def process_data():
    try:
        if session['username']:    
            method='input'
            if session['input_status'] == 'add_more':
                return redirect(url_for("app_ann.input"))

            elif session['input_status'] == "done":
                old_data = input_results.query.all()
                for data_instance in old_data:
                    db.session.delete(data_instance)

                inputs = metal_inputs.query.all()
                data = [(value.lat, value.long, value.cd, value.cr, value.ni, value.pb, value.zn, value.cu, value.co) for value in inputs]
                #print(data)
                input_set = pd.DataFrame(data, columns=["lat", "long", "cd", "cr", "ni", "pb", "zn", "cu", "co"])
                X = input_set.iloc[:, 2:].values
                #print(X)

                class_prediction = ann_c.predict(X)
                y_predicted_classes = np.argmax(class_prediction, axis=1)
                #print(class_prediction)
                decoded_predicted_classes = class_encoder.inverse_transform(y_predicted_classes)
                print(decoded_predicted_classes)
                reg_prediction = ann_r.predict(X)
                print(reg_prediction)

                input_set['predicted_mCdeg'] = reg_prediction
                input_set['predicted_class'] = decoded_predicted_classes
                print(input_set)
                
                data_to_insert = input_set.to_dict(orient='records')
                new_data = [input_results(**data) for data in data_to_insert]
                db.session.add_all(new_data)
                db.session.commit()
                db.session.close()
                return redirect( url_for("app_ann.view", mthd=method))
        else:
            return "User is not logged in!"
    except KeyError:
        return redirect(url_for('app_ann.login')) 

#UPLOADING FILES METHOD
@app_ann.route('/upload', methods=['POST', 'GET'])
def upload():
    try:
        if session['username']:
            uploads_folder = current_app.config['UPLOAD_DIRECTORY']
            extentions = current_app.config['ALLOWED_EXTENSIONS']
            try:
                if request.method == 'POST':
                
                    file = request.files['file']
                    extention = os.path.splitext(file.filename)[1]
                    print(extention)
                    if file:
                        if extention not in extentions:
                            return "File format not supported! Please upload pdf, excel or csv files."
                        file.save(os.path.join(
                            uploads_folder, 
                            secure_filename(file.filename)
                    
                        ))
                        file_name = secure_filename(file.filename)
                        return redirect(url_for('app_ann.read_file', new_file=file_name))
                    else:
                        return render_template('index-soil-prediction.html')
                else:
                    return render_template('index-soil-prediction.html')
                
            except RequestEntityTooLarge:
                return "File is too large than the 20MB limit!"
        else:
            return "User is not logged in!"
    except KeyError:
        return redirect(url_for('app_ann.login'))

@app_ann.route("/read_file/<new_file>")
def read_file(new_file):
    try:
        if session['username']:
            method='upload'

            old_data = file_data.query.all()
            for data_instance in old_data:
                db.session.delete(data_instance)

            data = []
            filepath = f'uploads/{new_file}'
            with open(filepath) as file:
                csvfile = csv.reader(file)
                for row in csvfile:
                    data.append(row)
            
            final_set = []
            for value in data[1:]:
                list= []
                for each in value:
                    converted_val = float(each)
                    list.append(converted_val)
                    #print(type(converted_val))
                final_set.append(list)
            dataset = pd.DataFrame(final_set, columns=["lat", "long", "cd", "cr", "ni", "pb", "zn", "cu", "co"])
            X = dataset.iloc[:, 2:].values
            
            #PREDICTION
            class_prediction = ann_c.predict(X)
            y_predicted_classes = np.argmax(class_prediction, axis=1)
            #print(y_predicted_classes)
            decoded_predicted_classes = class_encoder.inverse_transform(y_predicted_classes)
            #print(decoded_predicted_classes)
            reg_prediction = ann_r.predict(X)
            print(reg_prediction)

            dataset['predicted_mCdeg'] = reg_prediction
            dataset['predicted_class'] = decoded_predicted_classes

            
            data_to_insert = dataset.to_dict(orient='records')
            new_data = [file_data(**data) for data in data_to_insert]
            db.session.add_all(new_data)
            db.session.commit()
            db.session.close()

            return redirect(url_for('app_ann.view', mthd=method))
        else:
            return "User is not logged in!"
    except KeyError:
        return redirect(url_for('app_ann.login'))

@app_ann.route("/view/<mthd>")
def view(mthd):
    try:
        if session['username']:
            if mthd == 'input':
                results = input_results.query.all()
            elif mthd == 'upload':
                results = file_data.query.all()

            return render_template('index-view.html', data=results)
        else:
            return "User is not logged in!"
    except KeyError:
        return redirect(url_for('app_ann.login'))
    
@app_ann.route('/download', methods=['GET'])
def download():
    try:
        if session['username']:
            data = file_data.query.all()

            if len(data) > 0:
                # Create a CSV file
                csv_filename = 'data.csv'
                with open(csv_filename, 'w', newline='') as csvfile:
                    fieldnames = ['id', 'Latitude', 'Longitude', 'Cd (mg/kg)', 'Cr (mg/kg)', 'Ni (mg/kg)', 'Pb (mg/kg)', 'Zn (mg/kg)', 'Cu (mg/kg)', 'Co (mg/kg)', 'Predicted class']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in data:
                        writer.writerow({'id': row.id, 'Latitude': row.lat,'Longitude': row.long, 'Cd (mg/kg)': row.cd, 'Cr (mg/kg)': row.cr, 'Ni (mg/kg)': row.ni, 'Pb (mg/kg)': row.pb, 'Zn (mg/kg)': row.zn, 'Cu (mg/kg)': row.cu, 'Co (mg/kg)': row.co, 'Predicted class': row.predicted_class})

                # Return the CSV file as a downloadable attachment
                return send_file(csv_filename, as_attachment=True, download_name='data.csv', mimetype='application/pdf')
            else:
                return redirect(url_for('app_ann.input'))

        else:
            return "User is not logged in!"
    except KeyError:
        return redirect(url_for('app_ann.login')) 