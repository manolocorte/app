# (c) 2007-2022 NIHPO, Inc.
#
# This file is part of NIHPO's Synthetic Health Data Platform [https://github.com/nihpo/SynthHealthData]
#
# This platform is free software: you can redistribute it and/or modify it under the terms of the Affero GNU General Public License as published by the Free Software Foundation, version 3.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the Affero GNU General Public License for more details.
# You should have received a copy of the Affero GNU General Public License along with this program.  If not, see http://www.gnu.org/licenses/agpl-3.0.txt
#
# Contact us (Jose.Lacal@NIHPO.com) for a commercial license to use the NIHPO Synthetic Health Data Platform, or if you're interested in licensing a customized version of this platform.
#

from celery import Celery
from flask_session import Session
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from .celery_utils import init_celery
import psycopg2
import psycopg2.extras
import flask_profiler
from werkzeug.middleware.profiler import ProfilerMiddleware

def make_celery(app_name=__name__):
    backend = "redis://localhost:6379/0"
    broker = backend.replace("0", "1")
    return Celery(app_name, backend=backend, broker=broker)

celery = make_celery()

bootstrap = Bootstrap()
moment = Moment()
babel = Babel()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
db = SQLAlchemy()

def create_app(settings_module='config.develop', url_server='nothing', app_name=__name__, **kwargs):
    app = Flask(app_name)
    # dashboard.bind(app)

    if kwargs.get("celery"):
        init_celery(kwargs.get("celery"), app)

    app.config.from_object(settings_module)

    app.config['URL_SERVER'] = url_server

    Session(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from CE_app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from CE_app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from CE_app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from CE_app.synth_person import bp as synth_person_bp
    app.register_blueprint(synth_person_bp, url_prefix='/synth_person')

    from CE_app.synth_phr import bp as synth_phr_bp
    app.register_blueprint(synth_phr_bp, url_prefix='/synth_phr')

    from CE_app.synth_trial import bp as synth_trial_bp
    app.register_blueprint(synth_trial_bp, url_prefix='/synth_trial')

    from CE_app.synth_sub import bp as synth_sub_bp
    app.register_blueprint(synth_sub_bp, url_prefix='/synth_sub')

    app.config["flask_profiler"] = {
        "enabled": True,
        "storage": {
            "engine": "sqlalchemy",
            "db_url": f"postgresql://{app.config['CT_DATABASE_USER']}:{app.config['CT_DATABASE_PASSWORD']}@{app.config['CT_DATABASE_HOST']}:{app.config['CT_DATABASE_PORT']}/flask_profiler"
        },
        "basicAuth":{
            "enabled": True,
            "username": app.config['CT_PROFILER_USER'],
            "password": app.config['CT_PROFILER_PASSWORD']
        },
        "ignore": [
            "^/static/.*"
        ]
    }
    flask_profiler.init_app(app)

    if app.config['PROFILE']:
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
    

    with app.app_context():
        con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
            user = current_app.config["CT_DATABASE_USER"],
            password = current_app.config["CT_DATABASE_PASSWORD"],
            host = current_app.config["CT_DATABASE_HOST"],
            port = current_app.config["CT_DATABASE_PORT"])
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        app.config['CT_POSTGRESQL_CUR'] = cur
        app.config['CT_POSTGRESQL_CON'] = con
    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])

from CE_app import models