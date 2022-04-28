import gunicorn_hooks
# 并行工作进程数
workers = 1
# 指定每个工作者的线程数
threads = 4
# 监听内网端口
bind = '192.168.1.194:8000'
# 设置守护进程,将进程交给supervisor管理
daemon = 'false'
# 设置最大并发量
worker_connections = 2000
# 设置进程文件目录
pidfile = '/var/run/gunicorn.pid'
# 设置访问日志和错误信息日志路径
accesslog = '/var/log/gunicorn_acess.log'
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
errorlog = '/var/log/gunicorn_error.log'
# 设置日志记录水平
loglevel = 'debug'
raw_env = ["CONFIG=prod"]
on_starting = gunicorn_hooks.on_start
on_exit = gunicorn_hooks.on_exit

