"""
    :author: xiaoyicai.
    :date: 2021/05/09.
"""

from flask import Blueprint

home_view = Blueprint("home_view", __name__)
from app.home import homeview
