import os
from flask import Flask
from .views import upload
from .views import auth

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', #TODO: Need to change this to a randomized value in deployment
        DATABASE=os.path.join(app.instance_path, 'flowers.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #image serving
    UPLOAD_FOLDER = 'src/static/images/'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1080 * 1080

    #default routing test
    @app.route('/test')
    def test():
        return "This is a standard test."

    #DATABASE code?
    from . import db
    db.init_app(app)

    #REGISTER BLUEPRINT
    app.title = "Flowershop"
    app.register_blueprint(upload.upload)
    app.add_url_rule('/', endpoint='index')
    app.register_blueprint(auth.bp)

    return app
