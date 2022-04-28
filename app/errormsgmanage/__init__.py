"""
@File:__init__.py.py
@author:zhanfei
@date: 2021/11/23
"""

from flask import Blueprint

errormsgmanage = Blueprint("errormsgmanage", __name__)

from app.errormsgmanage import views