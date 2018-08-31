# coding:utf-8

from flask import Blueprint
from flask import render_template, request

from .models import *

app = Blueprint('accounts', __name__, template_folder='templates', url_prefix='/accounts')


@app.route("/")
def index_view():
    return render_template("index.html")
