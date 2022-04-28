"""
@File:__init__.py.py
@author:yangwuxie
@date: 2021/01/13
"""
from flask import Blueprint

teststep = Blueprint("teststep", __name__)


from app.teststep import views