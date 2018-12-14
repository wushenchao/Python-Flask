# pylint: disable=C,R,W
"""Package's main module!"""
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os

from flask import Flask, redirect
from flask_appbuilder import AppBuilder, IndexView, SQLA
from flask_appbuilder.baseviews import expose
from flask_compress import Compress
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.contrib.fixers import ProxyFix

from superset import config
from superset.connectors.connector_registry import ConnectorRegistry
from superset.security import SupersetSecurityManager


APP_DIR = os.path.dirname(__file__)
CONFIG_MODULE = os.environ.get('SUPERSET_CONFIG', 'superset.config')

if not os.path.exists(config.DATA_DIR):
    os.makedirs(config.DATA_DIR)

# with open(APP_DIR + '/static/assets/backendSync.json', 'r') as f:
#     frontend_config = json.load(f)

app = Flask(__name__)
app.config.from_object(CONFIG_MODULE)
conf = app.config


for bp in conf.get('BLUEPRINTS'):
    try:
        print("Registering blueprint: '{}'".format(bp.name))
        app.register_blueprint(bp)
    except Exception as e:
        print('blueprint registration failed')
        logging.exception(e)

if conf.get('SILENCE_FAB'):
    logging.getLogger('flask_appbuilder').setLevel(logging.ERROR)

if app.debug:
    app.logger.setLevel(logging.DEBUG)  # pylint: disable=no-member
else:
    # In production mode, add log handler to sys.stderr.
    app.logger.addHandler(logging.StreamHandler())  # pylint: disable=no-member
    app.logger.setLevel(logging.INFO)  # pylint: disable=no-member
logging.getLogger('pyhive.presto').setLevel(logging.INFO)

db = SQLA(app)

# pessimistic_connection_handling(db.engine)

# cache = setup_cache(app, conf.get('CACHE_CONFIG'))
# tables_cache = setup_cache(app, conf.get('TABLE_NAMES_CACHE_CONFIG'))

migrate = Migrate(app, db, directory=APP_DIR + '/migrations')


if conf.get('WTF_CSRF_ENABLED'):
    csrf = CSRFProtect(app)
    csrf_exempt_list = conf.get('WTF_CSRF_EXEMPT_LIST', [])
    for ex in csrf_exempt_list:
        csrf.exempt(ex)


if app.config.get('UPLOAD_FOLDER'):
    try:
        os.makedirs(app.config.get('UPLOAD_FOLDER'))
    except OSError:
        pass

for middleware in app.config.get('ADDITIONAL_MIDDLEWARE'):
    app.wsgi_app = middleware(app.wsgi_app)


class MyIndexView(IndexView):
    @expose('/')
    def index(self):
        return redirect('/superset/welcome')


custom_sm = app.config.get('CUSTOM_SECURITY_MANAGER') or SupersetSecurityManager
if not issubclass(custom_sm, SupersetSecurityManager):
    raise Exception(
        """Your CUSTOM_SECURITY_MANAGER must now extend SupersetSecurityManager,
         not FAB's security manager.
         See [4565] in UPDATING.md""")


def get_update_perms_flag():
    val = os.environ.get('SUPERSET_UPDATE_PERMS')
    return val.lower() not in ('0', 'false', 'no') if val else True


appbuilder = AppBuilder(
    app,
    db.session,
    base_template='superset/base.html',
    indexview=MyIndexView,
    security_manager_class=custom_sm,
    update_perms=get_update_perms_flag(),
)


security_manager = appbuilder.sm

results_backend = app.config.get('RESULTS_BACKEND')

# Registering sources
module_datasource_map = app.config.get('DEFAULT_MODULE_DS_MAP')
module_datasource_map.update(app.config.get('ADDITIONAL_MODULE_DS_MAP'))
ConnectorRegistry.register_sources(module_datasource_map)

# Flask-Compress
if conf.get('ENABLE_FLASK_COMPRESS'):
    Compress(app)

from superset import views
