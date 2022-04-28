"""
@File:__init__.py.py
@author:zhanfei
@date: 2021/03/31
"""

from flask import Blueprint

publishmanage = Blueprint("publishmanage", __name__)

from app.publishmanage import views