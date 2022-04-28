# 作者       ：yangwuxie
# 创建时间   ：2020/11/25 14:22

import os

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


class Config(object):
    SECRET_KEY = os.environ.get('SECRETE_KEY') or 'you will never guess'
    TOKEN_EXPIRATION = 7200
    TEMPLATES_AUTO_RELOAD = True
    JSON_AS_ASCII = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(

        "DATABASE_URL") or "mysql+pymysql://root:123456@localhost:3306/platform?charset=utf8"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 3
    DEBUG = True
    Dingtalk_access_token = "https://oapi.dingtalk.com/robot/send?access_token=69b4e53009f7f36c0216a0df6fd8c5c85af0a77bb2201968da5d4da0d298e04c"
    APP_HOST = "https://test.wxb.com.cn/substation"
    SCHEDULER_API_ENABLED = True
    SCHEDULER_JOBSTORES = {

        'default': SQLAlchemyJobStore(url="mysql+pymysql://root:123456@localhost:3306/platform?charset=utf8")}

    # SCHEDULER_EXECUTORS = {
    #     'default': {'type': 'threadpool', 'max_workers': 20}
    # }


class ProdConfig():
    SECRET_KEY = os.environ.get('SECRETE_KEY') or 'you will never guess'
    TOKEN_EXPIRATION = 7200
    TEMPLATES_AUTO_RELOAD = True
    JSON_AS_ASCII = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        # online_database
        "DATABASE_URL") or "mysql+pymysql://root:123456@192.168.1.194:3306/rhinoplatform?charset=utf8"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 3
    DEBUG = False
    Dingtalk_access_token = "https://oapi.dingtalk.com/robot/send?access_token" \
                            "=69b4e53009f7f36c0216a0df6fd8c5c85af0a77bb2201968da5d4da0d298e04c "
    APP_HOST = "https://test.wxb.com.cn/substation"
    SCHEDULER_API_ENABLED = True
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(
            tablename="apscheduler_jobs",
            url="mysql+pymysql://root:123456@192.168.1.194:3306/rhinoplatform?charset=utf8")
    }
    SCHEDULER_TIMEZONE = "Asia/Shanghai"
    # 发布相关配置
    UPLOAD_FOLDER1 = r'/home/pyproject/upload/publishmanage/afterReport'
    UPLOAD_FOLDER2 = r'/home/pyproject/upload/publishmanage/afterImageTask'
    UPLOAD_FOLDER3 = r'/home/pyproject/upload/publishmanage/frontReport'
    UPLOAD_FOLDER4 = r'/home/pyproject/upload/publishmanage/frontImageTask'
    # 邮件相关配置
    MAIL_SERVER = 'smtp.mxhichina.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'tester@ideacome.com'
    MAIL_PASSWORD = 'Test.123'
    MAIL_DEFAULT_SENDER = 'tester@ideacome.com'


ConfigMap = {
    "test": Config,
    "prod": ProdConfig,
}

