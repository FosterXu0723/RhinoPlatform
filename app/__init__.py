# coding=utf-8
# 作者       ：yangwuxie
# 创建时间   ：2020/11/25 14:19
import atexit
from flask import request, Response
import sys

from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from common.Log import log, errorLog
from flask.signals import got_request_exception
from config import ConfigMap
import os

from core.notice.DIngtalkNotice import sendMsg

db = SQLAlchemy()

scheduler = APScheduler()
mail = Mail()
login = LoginManager()
login.login_view = 'login'


def before_request(sender):
    """
    处理app请求前的事件
    :param sender: app
    :return:
    """
    pass


def _after_request(response):
    """
    为了解决Chrome版本升级之后出现的跨域请求失败的问题，采用此解决办法
    详见：https://juejin.cn/post/6844904088774115341
    :param response: Flask.Response对象
    :return: Flask.Response对象
    """
    # response.headers 是werkzeug.datastructures.Headers对象，不能用简单的字典处理
    if "Set-Cookie" in response.headers.keys():  # 现在已经存在Set-Cookie字段，这个时候更新
        response.headers.add("Set-Cookie", "SameSite=None; Secure")
    else:
        response.headers.extend(
            {"Access-Control-Request-Method": "GET,PUT,POST", "Access-Control-Request-Headers": "X-Custom-Header"})
    return response


def get_request_exception(sender, **kwargs):
    """
    处理请求异常
    :param sender: app
    :param kwargs: {exception=e}
    :return:
    """
    sender.log = errorLog
    msg = "请求发生异常,请求路径为: {}，异常信息为: {}".format(request.path, kwargs.get("exception"))
    sender.log.error(msg)
    sendMsg(title="请求异常通知Error", msg=msg)


def create_app():
    app = Flask(__name__)
    cf = os.path.exists("./product.d")
    if not cf:  # 表示dev环境
        app.config.from_object(ConfigMap.get("test"))
        log.info("获取到test配置文件")
    else:  # 表示是prod环境
        app.config.from_object(ConfigMap.get('prod'))
        log.info("获取到prod配置文件")
    scheduler_init(app)
    # app.app_context().push()
    with app.app_context():
        db.init_app(app)
    got_request_exception.connect(get_request_exception)
    # app.after_request(_after_request)
    CORS(app, supports_credentials=True)  # 允许跨域

    mail.init_app(app)

    from .users import user as user_blueprint
    from .projects import projects as project_blueprint
    from .interface import interface as interface_blueprint
    from .testcase import testcase as testcase_blueprint
    from .teststep import teststep as teststep_blueprint
    from .tctransform import tctransform as tctransform_blueprint
    from .testtools import testtools as testtools_blueprint
    from .publishmanage import publishmanage as publishmanage_blueprint
    from .task import task

    from .testreport import testreport as testreport_blueprint

    from .home import home_view as home_view_blueprint
    from .logmanage import logmanage as logmanage_blueprint
    from .errormsgmanage import errormsgmanage as errormsgmanage_blueprint
    from .commonapi import commonapi as commonapi_blueprint

    app.register_blueprint(user_blueprint)
    app.register_blueprint(project_blueprint, url_prefix='/projects')
    app.register_blueprint(interface_blueprint, url_prefix='/interface')
    app.register_blueprint(testcase_blueprint, url_prefix='/testcase')
    app.register_blueprint(teststep_blueprint, url_prefix='/teststep')
    app.register_blueprint(tctransform_blueprint, url_prefix='/tctf')
    app.register_blueprint(testtools_blueprint, url_prefix='/tools')
    app.register_blueprint(publishmanage_blueprint, url_prefix='/publish')
    app.register_blueprint(task, url_prefix="/task")

    app.register_blueprint(testreport_blueprint, url_prefix='/testreport')

    app.register_blueprint(home_view_blueprint, url_prefix='/about')
    app.register_blueprint(logmanage_blueprint, url_prefix='/log')
    app.register_blueprint(errormsgmanage_blueprint, url_prefix='/errormanage')
    app.register_blueprint(commonapi_blueprint, url_prefix='/commonapi')

    return app


def scheduler_init(app):
    """
    保证系统只启动一次定时任务
    :param app:
    :return:
    """
    if sys.platform == 'darwin' or sys.platform == 'linux':
        fcntl = __import__("fcntl")
        f = open('../scheduler.lock', 'wb')
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            scheduler.init_app(app)
        except:
            pass

        def unlock():
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()

        atexit.register(unlock)
    else:
        msvcrt = __import__('msvcrt')
        f = open('../scheduler.lock', 'wb')
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            scheduler.init_app(app)
        except:
            pass

        def _unlock_file():
            try:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            except:
                pass

        atexit.register(_unlock_file)
