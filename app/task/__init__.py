"""
@File: __init__.py
@author: guoweiliang
@date: 2021/5/10
"""

from flask import Blueprint

task = Blueprint("task", __name__)


from app.task import views
