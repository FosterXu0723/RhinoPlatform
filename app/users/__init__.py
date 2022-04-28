# 作者       ：yangwuxie
# 创建时间   ：2020/11/25 14:27

from flask import Blueprint

user = Blueprint("user", __name__)

from app.users import views,errors,auth