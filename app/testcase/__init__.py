"""
@File:__init__.py.py
@author:yangwuxie
@date: 2021/01/06
"""

from flask import Blueprint

testcase = Blueprint("testcase", __name__)

from app.testcase import views