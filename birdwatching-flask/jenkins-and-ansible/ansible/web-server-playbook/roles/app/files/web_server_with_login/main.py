import os
from flask import (
    Flask,
    jsonify
)
from login.login_register import login_register
from images.photo_uploader import photo_uploader
from dashboard.dashboard import dashboard
from models.models import db

secret_key=os.environ.get("SECRET_KEY")
dbname=os.environ.get("DB_NAME")
user=os.environ.get("DB_USER")
password=os.environ.get("DB_PASSWORD")
host=os.environ.get("DB_HOST")
port=os.environ.get("DB_PORT")

app = Flask(__name__)
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

app.secret_key = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{user}:{password}@{host}/{dbname}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # If enabled, all insert, update, and delete operations
# on models are recorded This adds a significant amount of overhead to every session

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(login_register, url_prefix="")
app.register_blueprint(photo_uploader, url_prefix="/upload")
app.register_blueprint(dashboard, url_prefix="/")

if __name__ == '__main__':
    app.run(debug=True)
