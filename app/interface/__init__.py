"""
@File:__init__.py.py
@author:yangwuxie
@date: 2020/12/28
"""

from flask import Blueprint

interface = Blueprint('interface',__name__)

from app.interface import views