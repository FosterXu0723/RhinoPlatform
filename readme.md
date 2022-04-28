## 快速开始    
1. git clone 完整代码
2. 删除migrations文件夹，自己新建空的migration文件夹，文件名不可修改
3. 配置config.py中的SQLALCHEMY_DATABASE_URI为自己开发环境本地配置
4. python db_migrate db init/python db_migrate db migrate/python db_migrate db upgrade
5. 完成初始化之后，暂时采用手动插入admin用户的方法，后续脚本执行
6. 启动服务 gunicorn -c gunicorn.conf.py manage:app
    > 服务器日志存储在/var/log/目录下，gunicorn_access.log/gunicorn_error.log。建议本地开发不要用gunicorn启动服务，直接在manage.py中app.run()，若非要用gunicorn命令启动，则:gunicorn -w 2 -b :8000 manage:app


## 注意事项  
1.  类型： 
    - 前端form-data传递参数，后端request.form接收参数，默认为str，若想使用原始类型，须手动转型
2.  flask对于http参数的处理：
    - 当request content-type为application/json时，用request.get_json()获取请求参数
    - 当request content-type为x-www-form-urlencoded时，用request.form获取请求参数
    - 当request method为get时，用request.args获取请求参数。拿到的请求参数全部为dict对象，具体值通过key获取
3. sqlalchemy：
    - db.relationship()中添加参数lazy=dynamic时，查询ref表中的字段得到的时一个查询对象，获取值需要进一步处理，类似于QueryObject.all()
4. 发布线上的时候需要确保db_migrate.py和manage.py及task.py文件中create_app()的参数修改为"prod"；同样，本地开发的时候注意一下create_app函数的参数，需要改成test，避免不必要的麻烦
5. 提交master的代码中，视图文件禁止携带print语句。切记检查！

## 线上项目启动
1. 查看当前分支是否是master分支，如有需要可以git pull远程master的最新代码到本地master,特别需要注意当前本地master的代码中是否按照注意事项中的第四个所说的书写
2. 启动项目需进入虚拟环境：source /home/pyproject/project/bin/activate
cd /home/pyproject/RhinoPlatform
3. 杀掉项目进程后使用gunicorn -c gunicorn.conf.py manage:app启动项目
4. 页面访问日志在/var/log/gunicorn_access.log下面，启动的日志在gunicorn_error.log