"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import  request, jsonify, url_for
from apiflask import APIFlask

from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin

from apiflask.fields import String, Boolean, List
from apiflask.schemas import EmptySchema

from models import db, User, Todo

app = APIFlask(__name__, docs_ui='rapidoc')

app.config["SERVERS"] = [{
    'name': 'API Server',
    'url': 'https://dotfortun-upgraded-train-q77644ggq6xfw4g-3000.preview.app.github.dev/'
}]
app.config['RAPIDOC_THEME'] = 'dark'

app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.post("/todos/user/<string:username>")
@app.input(EmptySchema)
@app.output(EmptySchema)
def create_user(username):
    db_user = User.query.filter_by(username=username).first()
    if not db_user:
        db.session.merge(User(username=username))
        db.session.commit()


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
