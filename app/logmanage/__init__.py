"""
@File:__init__.py.py
@author:zhanfei
@date: 2021/05/21
"""

from flask import Blueprint

logmanage = Blueprint("logmanage", __name__)

from app.logmanage import views
