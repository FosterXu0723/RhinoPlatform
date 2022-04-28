#  date:  2021/4/23
#  Author:  jinmu
#  Description:


from flask import Blueprint

testreport = Blueprint("testreport", __name__)


from app.testreport import views