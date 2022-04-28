"""
@File: gunicorn_hooks.py
@author: guoweiliang
@date: 2021/6/24
"""
import os

from gunicorn.arbiter import Arbiter
from gunicorn.config import Config
from common.Log import log


def on_start(server: Arbiter):
    """
    服务启动时的hook函数
    :param server:
    :return:
    """
    log.info(f"server start")
    """
    gunicorn服务启动时，raw_env参数携带的自定义环境变量只针对当前一次create_app生效
    当db_migrate.py中需要使用到create_app方法时，会出现os.environ无法获取之前设置的临时变量
    所以服务启动的时候持久化一个文件作为标记，表示当前是使用gunicorn启动
    """
    with open("./product.d", "w") as file:
        file.write("server.cfg.env")


def on_exit(server):
    """
    服务退出时候的hook函数
    :param server:
    :return:
    """
    log.info(f"server stopped")
    os.remove("./product.d")


def when_ready():
    """
    服务启动完成之后的hook函数
    :return:
    """
    pass


def pre_fork(server, work):
    pass


def post_fork(server, worker):
    pass


def post_worker_init(worker):
    pass


def worker_int(worker):
    pass


def worker_abort(worker):
    pass


def pre_exec(server):
    pass


def pre_request(worker, req):
    pass


def post_request(worker, req, environ, resp):
    pass


def child_exit(server, worker):
    pass


def worker_exit(server, worker):
    pass


def nworkers_changed(server, new_value, old_value):
    pass
