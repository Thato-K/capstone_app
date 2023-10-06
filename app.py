from flask import Flask, request, render_template, redirect, url_for
from create_table import db
from config import Config
from rf_config import rf_Config
from ann_folder.app_ann import app_ann
from rf_folder.app_rf import app_rf, init_app


app = Flask(__name__, template_folder="templates")
app.config['UPLOAD_FOLDER'] = 'uploads'  # Set UPLOAD_FOLDER for the Flask application

# Register blueprints and other configurations after setting UPLOAD_FOLDER
app.config.from_object(Config)
app.app_context().push()
db.init_app(app)

def init_app(app):
    UPLOAD_FOLDER = 'uploads'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.secret_key = 'contamination'


app.register_blueprint(app_ann, url_prefix="/ann")
app.register_blueprint(app_rf, url_prefix="/rf")

@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        model = request.form['model']

        if model == "ann_model":
            return redirect(url_for('app_ann.login'))
        elif model == "rf_model":
            return redirect(url_for('app_rf.login'))

    else:
        return render_template("homepage.html")



if __name__ == '__main__':
    init_app(app) 
    app.run(debug=True)