"""
@File:__init__.py.py
@author:zhanfei
@date: 2021/01/06
"""

from flask import Blueprint

tctransform = Blueprint("tctransform", __name__)

from app.tctransform import views