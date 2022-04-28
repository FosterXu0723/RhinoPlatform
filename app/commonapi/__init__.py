"""
@File:__init__.py.py
@author:zhanfei
@date: 2021/12/3
"""

from flask import Blueprint

commonapi = Blueprint("commonapi", __name__)

from app.commonapi import views