#!/usr/bin/env python
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_openid import OpenID
from config import basedir


app = Flask(__name__)
# 获取配置信息
app.config.setdefault(
    'SQLALCHEMY_TRACK_MODIFICATIONS', True
)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
oid = OpenID(app, os.path.join(basedir, 'tmp'))

from app import routes, models
