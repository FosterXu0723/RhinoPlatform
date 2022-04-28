# 作者       ：yangwuxie
# 创建时间   ：2020/11/27 11:18

from flask import Blueprint

projects = Blueprint("projects",__name__)

from app.projects import views