# 作者       ：yangwuxie
# 创建时间   ：2020/11/25 14:23
from datetime import datetime

from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import Unicode, Float, LargeBinary
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login
from config import Config

# 任务和用例多对多的表
TaskCase = db.Table(
    "task_case",
    db.Column("task_id", db.Integer, db.ForeignKey("task.id"), primary_key=True),
    db.Column("case_id", db.Integer, db.ForeignKey("testcase.id"), primary_key=True)
)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    updatetime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    operator = db.Column(db.String(128))
    delete_status = db.Column(db.SmallInteger, default=1)  # 1:正常 2:删除
    delete_at = db.Column(db.DateTime)
    # db.relation相当于letf join，可以查询与当前对象关联的其他表对象
    projects = db.relationship("Project", backref="user")
    interfaces = db.relationship("Interface", backref="user")

    # token = db.Column(db.String(32), index=True, unique=True)
    # token_expiration = db.Column(db.DateTime)  # token过期时间

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id,
                "username": self.username,
                "updatetime": self.updatetime,
                "operator": self.operator}

    @staticmethod
    def create_token(user_id):
        s = Serializer(Config.SECRET_KEY, expires_in=Config.TOKEN_EXPIRATION)
        token = s.dumps({'id': user_id}).decode('ascii')
        return token

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Project(db.Model):  # 项目
    __tablename__ = 'projects'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    project_user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    project_desc = db.Column(db.String(252))
    project_name = db.Column(db.String(252), unique=True)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    interface = db.relationship("Interface", backref="project", lazy='dynamic')
    env = db.relationship("ProjectEnv", backref="project_env", lazy='dynamic')
    status = db.Column(db.Boolean(), default=False)
    module = db.Column(db.VARCHAR(256), comment="项目模块")

    def __repr__(self):
        return '<Project {}>'.format(self.project_name)

    def to_dict(self):
        def convertList(content):
            return content.split(",") if content is not None else []

        data = {
            "id": self.id,
            "projectName": self.project_name,
            "projectDesc": self.project_desc,
            "projectOwner": self.project_user_id,
            "createTime": self.create_time,
            "updateTime": self.update_time,
            "projectStatus": self.status,
            "modules": convertList(self.module)
        }
        return data


class Testcase(db.Model):  # 测试用例
    """
    用例依赖casestep，casestep依赖接口
    """
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    projects_id = db.Column(db.Integer(), db.ForeignKey('projects.id'))
    case_name = db.Column(db.String(252), comment="用例名称")
    open_status = db.Column(db.Boolean, default=True, comment="用例开启状态，true为开启，False为关闭")
    case_run_total = db.Column(db.Integer, server_default="0", comment="用例执行次数")
    case_pass_total = db.Column(db.Integer, server_default="0", comment="用例执行成功次数")
    case_last_runtime = db.Column(db.DateTime, comment="用例最后一次执行时间")
    steps = db.relationship("TestStep", backref="testcase", lazy="dynamic")
    create_at = db.Column(db.DateTime, comment="创建日期")
    update_at = db.Column(db.DateTime, onupdate=datetime.now, comment="更新时间")
    module = db.Column(db.VARCHAR(256), comment="用例所属模块")
    author = db.Column(db.String(20), comment="用例创建人")

    def __repr__(self):
        return self.case_name

    def to_dict(self):
        return {
            "id": self.id,
            "projectId": self.projects_id,
            "caseName": self.case_name,
            "openStatus": self.open_status,
            "caseRunTotal": self.case_run_total,
            "casePassTotal": self.case_pass_total,
            "caseLastRuntime": self.case_last_runtime,
            "createAt": self.create_at,
            "module": self.module,
            "author": self.author
        }


class TestStep(db.Model):
    """
    接口步骤表
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    step_name = db.Column(db.String(252), comment="步骤名称")
    case_step_index = db.Column(db.Integer, nullable=False, default="0", comment="接口测试用例步骤索引")
    testcase_id = db.Column(db.Integer, db.ForeignKey('testcase.id'), comment="关联的用例id")
    set_up_case = db.Column(db.Integer(), comment="前置用例")
    tear_down_case = db.Column(db.Integer(), comment="后置用例")
    # step实际相当于接口，当有接口关联的时候不允许再添加接口相关的参数
    interface_id = db.Column(db.Integer, db.ForeignKey("interfaces.id"), comment="关联的接口id，一对一的关系")
    step_api_path = db.Column(db.String(252), comment="api路径")
    step_api_method = db.Column(db.String(10), comment="api请求方式")
    step_api_header = db.Column(db.PickleType, comment="api请求头")
    step_api_data = db.Column(db.PickleType, comment="api请求体")
    step_api_extract = db.Column(db.PickleType, comment="api提取参数")
    step_api_assert = db.Column(db.PickleType, comment="api断言")
    step_api_pass = db.Column(db.Boolean, comment="step通过状态")
    delete_at = db.Column(db.DateTime, comment="step删除时间，为空表示正常使用")

    def to_dict(self):
        return {
            "stepId": self.id,
            "stepIndex": self.case_step_index,
            "stepName": self.step_name,
            "caseId": self.testcase_id,
            "interfaceId": self.interface_id,
            "stepPath": self.step_api_path,
            "stepMethod": self.step_api_method,
            "stepHeader": self.step_api_header,
            "stepData": self.step_api_data,
            "stepExtract": self.step_api_extract,
            "stepAssert": self.step_api_assert,
            "setUpCase": self.set_up_case
        }


class Interface(db.Model):  # 接口表
    __tablename__ = 'interfaces'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    # model_id = db.Column(db.Integer(), db.ForeignKey('models.id'))
    projects_id = db.Column(db.Integer(), db.ForeignKey('projects.id'))
    interface_name = db.Column(db.String(252), nullable=False)
    interface_url = db.Column(db.String(252), nullable=False)  # 接口路径
    interface_meth = db.Column(db.String(252), default='GET')
    interface_headers = db.Column(db.String(252), nullable=False)
    interface_user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    interfacetype = db.Column(db.String(32), default='http')
    interface_param = db.Column(db.PickleType)
    status = db.Column(db.SMALLINT, default=0)  # 0:未开始，1：进行中 2：已完成
    delete_at = db.Column(db.DateTime, default=None)  # delete_at 有内容表示删除状态

    step = db.relationship("TestStep", backref="interface", uselist=False)

    def __repr__(self):
        return self.interface_name

    def to_dict(self):
        data = {
            'interfaceId': self.id,
            'interfaceName': self.interface_name,
            'project': self.projects_id,
            'interfaceParams': self.interface_param,
            'interfaceOwner': self.interface_user_id,
            'interfaceMethdod': self.interface_meth,
            'interfaceHeader': self.interface_headers,
            'interfacePath': self.interface_url,
            'interfaceType': self.interfacetype,
            'status': self.status
        }
        return data


# 定时任务表
class Task(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer(), comment="创建者id")
    task_name = db.Column(db.String(52), comment="任务名称")
    task_start = db.Column(db.DateTime(), comment="任务执行时间")
    task_type = db.Column(db.String(10), comment="任务类型，date一次性任务，interval循环执行的任务")
    create_at = db.Column(db.DateTime(), default=datetime.now(), comment="创建时间")
    task_status = db.Column(db.Boolean(), default=True, comment="默认正常状态")
    update_at = db.Column(db.DateTime(), comment="更新时间")
    task_cases = db.relationship("Testcase", secondary=TaskCase, backref="tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "owner": self.owner,
            "taskName": self.task_name,
            "taskStart": self.task_start,
            "createAt": self.create_at,
            "taskType": self.task_type,
            "taskStatus": self.task_status,
        }


# case执行结果表
class CaseResult(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    caseId = db.Column(db.Integer(), comment="用例id")
    assertResult = db.Column(db.TEXT(), comment="断言结果")
    exception = db.Column(db.TEXT(), comment="异常信息")
    create_at = db.Column(db.DateTime(), default=datetime.now(), comment="创建时间")
    caseTask = db.Column(db.Integer(), comment="当前执行结果所属任务")
    case_task_run_index = db.Column(db.Integer(), comment="用例所属任务执行次数")
    caseFlag = db.Column(db.Boolean(), comment="当前用例结果")

    def to_dict(self):
        return {
            "id": self.id,
            "caseId": self.caseId,
            "assertResult": self.assertResult,
            "exception": self.exception,
            "create_at": self.create_at,
            "caseTask": self.caseTask,
            "case_task_run_index": self.case_task_run_index,
            "caseFlag": self.caseFlag,
        }


class ReportResult(db.Model):
    __tablename__ = 'reportresult'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    taskId = db.Column(db.Integer(), nullable=False, comment='对应taskId')
    reportName = db.Column(db.String(256), comment='报告名称')
    reportStatus = db.Column(db.Integer(), nullable=False, default=1, comment='报告状态，1表示成功，2表示失败')
    creatDate = db.Column(db.DateTime(), comment="报告生成日期", default=datetime.now)
    totalCount = db.Column(db.Integer(), comment='用例总数')
    passCount = db.Column(db.Integer(), comment='通过用例数')
    failCount = db.Column(db.Integer(), comment='失败用例数', default=0)
    errorCount = db.Column(db.Integer(), comment='错误用例数', default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "taskId": self.taskId,
            "reportName": self.reportName,
            "reportStatus": self.reportStatus,
            "creatDate": self.creatDate,
            "totalCount": self.totalCount,
            "passCount": self.passCount,
            "failCount": self.failCount,
            "errorCount": self.errorCount,
        }


# 定时任务结果统计表
class HomeView(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    projectId = db.Column(db.Integer, comment='项目id')
    projectName = db.Column(db.String(255))
    taskId = db.Column(db.Integer())
    taskName = db.Column(db.String(255))
    createtime = db.Column(db.DateTime(), default=datetime.now())
    successTotal = db.Column(db.Integer())
    failTotal = db.Column(db.Integer())
    total = db.Column(db.Integer())
    passRate = db.Column(db.String(255))


class TaskResult(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    create_at = db.Column(db.DateTime(), default=datetime.now(), comment="创建时间")
    task_id = db.Column(db.Integer(), nullable=False, comment="所属task")
    task_run_index = db.Column(db.Integer(), default=0, comment="所属task第几次执行")
    task_case_status = db.Column(db.TEXT(), comment="task所属case执行情况，pass/failed")
    task_case_assert = db.Column(db.TEXT(), comment="task所属case断言情况")


# class TestResult(db.Model):  # 测试结果表
#     __tablename__ = 'tstresults'
#     id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
#     Test_user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
#     test_num = db.Column(db.Integer())
#     pass_num = db.Column(db.Integer())
#     fail_num = db.Column(db.Integer())
#     Exception_num = db.Column(db.Integer())
#     can_num = db.Column(db.Integer())
#     wei_num = db.Column(db.Integer())
#     projects_id = db.Column(db.Integer(), db.ForeignKey('projects.id'))
#     test_time = db.Column(db.DateTime(), default=datetime.datetime.now())
#     hour_time = db.Column(db.Integer())
#     test_rep = db.Column(db.String(252))
#     test_log = db.Column(db.String(252))
#     status = db.Column(db.Boolean(), default=False)
#
#     def __repr__(self):
#         return str(self.id)
#
#
# class Model(db.Model):  # 模块，有的接口是根据模块来划分的
#     __tablename__ = 'models'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     model_name = db.Column(db.String(256))
#     model_user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
#     Interfacetest = db.relationship('InterfaceTest', backref='models', lazy='dynamic')
#     Interface = db.relationship('Interface', backref='models', lazy='dynamic')
#     status = db.Column(db.Boolean(), default=False)
#
#     def __repr__(self):
#         return self.model_name
#
#
# class EmailReport(db.Model):  # 邮件通知推送配置
#     __tablename__ = 'emailReports'
#     id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
#     email_re_user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
#     send_email = db.Column(db.String(64))  # 发送邮箱的邮件
#     send_email_password = db.Column(db.String(64))  # 发送邮件的密码
#     stmp_email = db.Column(db.String(64))  # stmp服务器
#     port = db.Column(db.Integer())  # 端口号
#     to_email = db.Column(db.String())  # 收件人
#     default_set = db.Column(db.Boolean(), default=False)  # 默认
#     status = db.Column(db.Boolean(), default=False)  # 状态
#
#     def __repr__(self):
#         return self.send_email
#
#


class ProjectEnv(db.Model):  # 测试环境
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    env_name = db.Column(db.String(252), comment="环境名称")
    host = db.Column(db.String(252), comment="环境域名地址")  # 地址
    header = db.Column(db.PickleType, comment="通用请求头")
    database = db.Column(db.String(252), comment="数据库名称")  # 数据库
    db_port = db.Column(db.String(252), comment="数据库端口")  # 数据库服务端口号
    db_type = db.Column(db.String(252), comment="数据库类型")
    db_host = db.Column(db.String(252), comment="数据库主机")  # 数据库主机
    db_user = db.Column(db.String(32), comment="数据库用户名")
    db_password = db.Column(db.String(32), comment="数据库密码")
    project = db.Column(db.Integer(), db.ForeignKey('projects.id'))  # 环境对应的项目

    def __repr__(self):
        return str(self.id)

    def to_dict(self):
        return {
            "envId": self.id,
            "projectEnvName": self.env_name,
            "projectHost": self.host,
            "projectHeader": self.header,
            "projectDbName": self.database,
            "projectDbUrl": self.db_host,
            "projectDbType": self.db_type,
            "projectDbPort": self.db_port,
            "projectDbUser": self.db_user,
            "projectDbPassword": self.db_password,
            "projectId": self.project
        }


#
#
# class TestcaseResult(db.Model):  # 测试用例结果
#     __tablename__ = 'testcaseresults'
#     id = db.Column(db.Integer, primary_key=True)
#     case_id = db.Column(db.Integer, db.ForeignKey('interfacetests.id'), nullable=True)
#     result = db.Column(db.String(252))
#     date = db.Column(db.DateTime(), default=datetime.datetime.now())
#     testevir = db.Column(db.Integer, db.ForeignKey('ceshihuanjing.id'), nullable=True)
#
#     def __repr__(self):
#         return str(self.id)
#
#
# class Parameter(db.Model):  # 参数
#     __tablename__ = 'parames'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     interface_id = db.Column(db.Integer, db.ForeignKey("interfaces.id"))  # 接口id
#     parameter_type = db.Column(db.String(64))  # 参数类型
#     parameter_name = db.Column(db.String(64))  # 参数名字
#     necessary = db.Column(db.Boolean(), default=False)  # 是否必须
#     type = db.Column(db.Integer(), default=0)  # 类型,返回还是传参，入参为0  出参为1
#     status = db.Column(db.Boolean(), default=False)  # 状态
#     default = db.Column(db.String(63))  # 示例
#     desc = db.Column(db.String(252))  # 参数描述
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#
#     def __repr__(self):
#         return str(self.id)
#
#
# class CaseGeneral(db.Model):
#     '''测试用例和通用参数关系'''
#     __tablename__ = 'casegenerals'
#     id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
#     case = db.Column(db.Integer(), db.ForeignKey("interfacetests.id"))
#     general = db.Column(db.Integer(), db.ForeignKey("generalconfigurations.id"))
#     filed = db.Column(db.String(252))
#
#     def __repr__(self):
#         return str(self.id)
# 
# 
class TcTransForm(db.Model):
    """生成CSV文件表"""
    __tablename__ = 'tctransforms'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    case_file_name = db.Column(db.String(252), nullable=False, comment="用例文件名称")
    case_belong_module = db.Column(db.String(252), nullable=False, comment="用例文件归属模块")
    operators = db.Column(db.String(252), nullable=True, comment="操作者")
    file_url = db.Column(db.String(252), nullable=False, comment="CSV文件生成地址")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="生成时间")

    def to_dict(self):
        data = {
            'transformId': self.id,
            'caseFileName': self.case_file_name,
            'caseBelongModule': self.case_belong_module,
            'operator': self.operators,
            'fileUrl': self.file_url,
            'createTime': self.create_time
        }
        return data


# 
#    
class TransForm_Modules(db.Model):
    """用例文件归属模块"""
    __tablename__ = 'transform_modules'
    id = db.Column(db.Integer(), primary_key=True)
    MainMenus = db.Column(db.String(252), nullable=False, comment="主菜单")
    ChildMenus = db.Column(db.String(252), nullable=False, comment="子菜单")
    MenuStatus = db.Column(db.Integer(), nullable=True, default=1, comment="是否有效;1是有效,0是无效")

    def to_dict(self):
        data = {
            'id': self.id,
            'MainMenus': self.MainMenus,
            'ChildMenus': self.ChildMenus,
            'MenuStatus': self.MenuStatus
        }
        return data


class TestTools(db.Model):
    """上传测试工具表"""
    __tablename__ = 'testtools'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    tool_name = db.Column(db.String(252), nullable=False, comment="测试工具对外名称")
    tool_author = db.Column(db.String(252), nullable=False, comment="测试工具创作人")
    tool_url = db.Column(db.String(252), nullable=False, comment="测试工具地址")
    tool_realname = db.Column(db.String(252), nullable=False, comment="测试工具实际名称")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="上传时间")
    delete_id = db.Column(db.Integer(), default=0, comment="是否删除,0否1是")

    def to_dict(self):
        data = {
            'toolId': self.id,
            'toolName': self.tool_name,
            'toolAuthor': self.tool_author,
            'toolUrl': self.tool_url,
            'fileName': self.tool_realname,
            'createTime': self.create_time,
            'deleteId': self.delete_id
        }
        return data


class PublishManage(db.Model):
    """发布管理测试报告数据表"""
    __tablename__ = 'publishmanage'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    task_development = db.Column(db.String(50), nullable=False, comment="发布任务归属的研发端")
    task_name = db.Column(db.String(252), nullable=False, comment="发布任务名称")
    task_business = db.Column(db.String(100), nullable=False, comment="发布任务归属的业务线")
    task_author = db.Column(db.String(100), nullable=False, comment="发布任务创建者")
    testreport_url = db.Column(db.String(252), nullable=False, comment="测试报告地址")
    testreport_realname = db.Column(db.String(252), nullable=False, comment="测试报告实际名称")
    task_date = db.Column(db.String(50), nullable=False, comment="发布任务时间")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    task_status = db.Column(db.String(50), nullable=False, comment="发布任务状态")
    require_name = db.Column(db.String(1000), nullable=False, comment="需求名称")
    image_url = db.Column(db.String(252), nullable=True, comment="邮件图片地址")
    image_realname = db.Column(db.String(252), nullable=True, comment="邮件图片实际名称")
    delete_id = db.Column(db.Integer(), default=0, comment="是否删除,0否1是")

    def to_dict(self):
        data = {
            'taskId': self.id,
            'taskDevelopment': self.task_development,
            'taskName': self.task_name,
            'taskBusiness': self.task_business,
            'taskAuthor': self.task_author,
            'testreportUrl': self.testreport_url,
            'fileName': self.testreport_realname,
            'taskDate': self.task_date,
            'createTime': self.create_time,
            'taskStatus': self.task_status,
            'requireName': self.require_name,
            'imageUrl': self.image_url,
            'imageName': self.image_realname,
            'deleteId': self.delete_id
        }
        return data


class PublishManage_AfterEndDetails(db.Model):
    """发布管理后端数据详情表"""
    __tablename__ = 'publishmanage_afterenddetails'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer(), nullable=False, comment="发布任务ID")
    require_name = db.Column(db.String(1000), nullable=False, comment="需求名称")
    after_developer = db.Column(db.String(252), nullable=True, comment="后端开发者")
    publish_project = db.Column(db.String(1000), nullable=True, comment="发布工程")
    publish_branch = db.Column(db.String(252), nullable=True, comment="发布分支")
    jar_name = db.Column(db.String(1000), nullable=True, comment="jar包")
    check_sql = db.Column(db.String(252), nullable=True, comment="是否有SQL")
    other_require = db.Column(db.String(1000), nullable=True, comment="其他要求")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")

    def to_dict(self):
        data = {
            'detailsId': self.id,
            'taskId': self.id,
            'requireName': self.require_name,
            'afterDeveloper': self.after_developer,
            'publishProject': self.publish_project,
            'publishBranch': self.publish_branch,
            'jarName': self.jar_name,
            'checkSql': self.check_sql,
            'otherRequire': self.other_require,
            'createTime': self.create_time,
        }
        return data


class PublishManage_FrontEndDetails(db.Model):
    """发布管理前端数据详情表"""
    __tablename__ = 'publishmanage_frontenddetails'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer(), nullable=False, comment="发布任务ID")
    require_name = db.Column(db.String(1000), nullable=False, comment="需求名称")
    front_developer = db.Column(db.String(252), nullable=True, comment="前端开发者")
    publish_project = db.Column(db.String(1000), nullable=True, comment="发布工程")
    publish_branch = db.Column(db.String(252), nullable=True, comment="发布分支")
    app_renew = db.Column(db.String(252), nullable=True, comment="是否需要更新APP")
    other_require = db.Column(db.String(1000), nullable=True, comment="其他要求")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")

    def to_dict(self):
        data = {
            'detailsId': self.id,
            'taskId': self.id,
            'requireName': self.require_name,
            'frontDeveloper': self.after_developer,
            'publishProject': self.publish_project,
            'publishBranch': self.publish_branch,
            'appRenew': self.app_renew,
            'otherRequire': self.other_require,
            'createTime': self.create_time,
        }
        return data


"""
apscheduler_jobs表，避免migrate的时候没有apscheduler_jobs表结构存在，删除任务表
"""


class SchdulerJob:
    __tablename__ = "apscheduler_jobs"
    id = db.Column(Unicode(191, _warn_on_bytestring=False), primary_key=True),
    next_run_time = db.Column(Float(25), index=True),
    job_state = db.Column(LargeBinary, nullable=False)



class PullError_Task(db.Model):
    """拉取线上报错信息任务表"""
    __tablename__ = 'pullerror_task'
    id = db.Column(db.Integer(), primary_key=True)
    task_startdate = db.Column(db.String(20), nullable=False, comment="拉取任务开始日期")
    task_enddate = db.Column(db.String(20), nullable=False, comment="拉取任务结束日期")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    task_status = db.Column(db.String(20), nullable=False, comment="周期处理状态")
    delete_id = db.Column(db.Integer(), default=0, comment="是否删除,0否1是")

    def to_dict(self):
        data = {
            'id': self.id,
            'taskStartDate': self.task_startdate,
            'taskendDate': self.task_enddate,
            'createTime': self.create_time,
            'taskStatus': self.task_status,
            'deleteId': self.delete_id
        }
        return data

class BaseDataSource(db.Model):
    """基础数据表"""
    __tablename__ = 'basedatasource'
    id = db.Column(db.Integer(), primary_key=True)
    fieldname = db.Column(db.String(20), nullable=False, comment="属性名称")
    fieldvalue = db.Column(db.String(50), nullable=False, comment="属性值")
    delete_id = db.Column(db.Integer(), default=0, comment="是否删除,0否1是")

    def to_dict(self):
        data = {
            'id': self.id,
            'fieldName': self.fieldname,
            'fieldValue': self.fieldvalue,
            'deleteId': self.delete_id
        }
        return data


class PullError_details(db.Model):
    """拉取线上报错信息详细表"""
    __tablename__ = 'pullerror_details'
    id = db.Column(db.Integer(), primary_key=True)
    task_id = db.Column(db.Integer(), nullable=False, comment="拉取任务ID")
    project_name=db.Column(db.String(20), nullable=True, comment="报错的工程")
    belong_bus=db.Column(db.String(20), nullable=True, comment="报错信息所属业务")
    error_class=db.Column(db.String(500), nullable=True, comment="报错的类")
    error_info=db.Column(db.String(5000), nullable=True, comment="报错信息")
    error_times=db.Column(db.String(20), nullable=True, comment="报错信息出现次数")
    error_date=db.Column(db.String(40), nullable=True, comment="报错信息出现日期")
    developer=db.Column(db.String(20), nullable=True, comment="开发人员")
    tester=db.Column(db.String(20), nullable=True, comment="测试人员")
    error_reason=db.Column(db.String(300), nullable=True, comment="错误原因")
    error_status = db.Column(db.String(20), nullable=True, comment="处理状态")
    pub_date = db.Column(db.String(20), nullable=True, comment="上线时间")
    error_remarks = db.Column(db.String(200), nullable=True, comment="备注")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    delete_id = db.Column(db.Integer(), default=0, comment="是否删除,0否1是")

    def to_dict(self):
        data = {
            'id': self.id,
            'taskID': self.task_id,
            'projectName': self.project_name,
            'belongBus': self.belong_bus,
            'errorClass': self.error_class,
            'errorInfo': self.error_info,
            'errorTimes': self.error_times,
            'errorDate': self.error_date,
            'developer': self.developer,
            'tester': self.tester,
            'errorReason': self.error_reason,
            'errorStatus': self.error_status,
            'pubDate': self.pub_date,
            'errorRemarks': self.error_remarks,
            'createTime': self.create_time,
            'deleteId': self.delete_id
        }
        return data


class ProjectBelongBus(db.Model):
    """项目和业务关系表"""
    __tablename__ = 'projectbelongbus'
    id = db.Column(db.Integer(), primary_key=True)
    business=db.Column(db.String(20), nullable=True, comment="所属业务")
    project=db.Column(db.String(20), nullable=True, comment="工程")
    developer=db.Column(db.String(20), nullable=True, comment="开发负责人")
    tester=db.Column(db.String(20), nullable=True, comment="测试负责人")
    delete_id = db.Column(db.Integer(), default=0, comment="是否删除,0否1是")

    def to_dict(self):
        data = {
            'id': self.id,
            'Business': self.business,
            'Project': self.project,
            'Developer': self.developer,
            'tester': self.developer,
            'deleteId': self.delete_id
        }
        return data


class StaffBasicInfo(db.Model):
    """人员基本信息表"""
    __tablename__ = 'staffbasicinfo'
    id = db.Column(db.Integer(), primary_key=True)
    name=db.Column(db.String(20), nullable=True, comment="人员姓名")
    role=db.Column(db.String(20), nullable=True, comment="人员角色")
    phone=db.Column(db.String(20), nullable=True, comment="人员电话")
    email=db.Column(db.String(50), nullable=True, comment="人员邮箱")
    delete_id = db.Column(db.Integer(), default=0, comment="是否删除,0否1是")

    def to_dict(self):
        data = {
            'id': self.id,
            'Name': self.name,
            'Role': self.role,
            'Phone': self.phone,
            'Email': self.email,
            'deleteId': self.delete_id
        }
        return data