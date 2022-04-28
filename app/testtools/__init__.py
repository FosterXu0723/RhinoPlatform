"""
@File:__init__.py.py
@author:zhanfei
@date: 2021/02/22
"""

from flask import Blueprint

testtools = Blueprint("testtools", __name__)

from app.testtools import views