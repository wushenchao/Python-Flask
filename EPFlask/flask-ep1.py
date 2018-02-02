#!/usr/bin/env python
from flask import Flask, request, render_template, abort, redirect, url_for

app = Flask(__name__)


@app.route('/')
def index():
    """URL重定向"""
    return redirect(url_for('show_user_profile'))


@app.route('/hello')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('index.html', name=name)


@app.route('/user')
@app.route('/user/<username>')
def show_user_profile(username=None):
    return 'User %s' % username


@app.route('/login', methods=['GET', 'POST'])
def login():
    return 'Hello World!'
    # if request.method == 'POST':
    #     print('post')
    # else:
    #     print('get')


if __name__ == '__main__':
    app.run(debug=True)

