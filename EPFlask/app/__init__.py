#!/usr/bin/env python

from flask import Flask

app = Flask(__name__)
# 获取配置信息
app.config.from_object('config')

from app import routes
