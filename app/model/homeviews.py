"""
    :author: xiaoyicai.
    :date: 2021/05/09.
    ：use: 首页相关的方法
"""

from app.utils import query_util
from app import db, create_app
from sqlalchemy import Column, Integer, String, SmallInteger, Boolean, text
from app.models import Project
from common.Log import log

app = create_app()
app.app_context().push()
with app.app_context():
    db.init_app(app)


def get_total():
    # 查询项目总数和用例总数

    # app.app_context().push()
    # res = []
    projects = db.session.execute("select count(*) as project from projects  ")
    project_count = query_util.result_to_dict(projects)[0]
    cases = db.session.execute("select count(*) as 'case' from `testcase` where open_status =1")
    case_count = query_util.result_to_dict(cases)[0]
    tasks = db.session.execute("select count(*) as 'scheduler' from `task`")
    task_count = query_util.result_to_dict(tasks)[0]
    res = dict(project_count, **case_count, **task_count)
    return res


def get_case_by_week():
    # 本周新增的用例数
    # if not app is current_app:
    #     app.app_context().push()
    total = db.session.execute("select count(*) as count from testcase  "
                               "where DATE_SUB(CURDATE(), INTERVAL 7 DAY) <= date(create_at)")
    total = query_util.result_to_dict(total)
    total = total[0]['count']
    return total


def get_case_by_week_project():
    # 每周 每个项目新增的用例数
    projects = db.session.execute("select id,project_name from projects  ")

    res = query_util.result_to_dict(projects)

    # db.session.remove()
    res_list = []
    for i in res:
        id_ = i['id']
        name = i['project_name']
        sql = "select count(*) as count from testcase where DATE_SUB(CURDATE(), " \
              "INTERVAL 7 DAY) <= date(create_at) and projects_id = {}"
        sql = sql.format(id_)

        total = db.session.execute(sql)
        # total = len(list(total))
        total = query_util.result_to_dict(total)
        total = total[0]['count']

        dict_ = {"id": i['id'], "name": name, "total": total}

        res_list.append(dict_)

    return res_list


def today():
    # 今日执行测试  今日测试工程  今日新增用例
    case_add_tody = db.session.execute("SELECT COUNT(*) as case_add_tody from testcase "


                                       "where TO_DAYS(`create_at`) = TO_DAYS(NOW()) and open_status =1")

    case_add_tody = query_util.result_to_dict(case_add_tody)[0]
    # cast {'case_add_tody': 1, 'case_run_tody': Decimal('19'), 'project_run_tody': 2} 去除Decimal
    case_run_tody = db.session.execute("SELECT CAST(ifnull((SUM(total)),0) as CHAR) as case_run_tody  from home_view "
                                       "where TO_DAYS(createtime) = TO_DAYS(NOW())")
    case_run_tody = query_util.result_to_dict(case_run_tody)[0]
    project_run_tody = db.session.execute("SELECT count(*) as project_run_tody from "
                                          "(SELECT projectId as project_count from home_view "
                                          "where TO_DAYS(createtime) = TO_DAYS(NOW()) GROUP BY projectId)m")
    project_run_tody = query_util.result_to_dict(project_run_tody)[0]
    res = dict(case_add_tody, **case_run_tody, **project_run_tody)
    return res


def caseTop():

    res_toprun = db.session.execute("SELECT n.caseId,testcase.case_name,n.pass,n.fail,n.count from (SELECT * ,SUM(pass+fail) as count from"
                                    "(SELECT caseId ,count(case WHEN caseFlag=1 then 1 END)  AS pass,"
                                    "count(case WHEN `caseFlag`=0 or caseFlag is null  then 2 END)  AS fail from case_result GROUP BY caseId)m "
                                    "GROUP BY m.caseId ORDER BY count desc,caseId desc LIMIT 10 )n LEFT JOIN testcase on n.caseId = testcase.id")


    res_toppass = db.session.execute("SELECT n.caseId,testcase.case_name,n.pass,n.fail,n.count,n.passrate from (SELECT * ,IFNULL(CONVERT(pass/count,decimal(10,2))*100,0)"
                                     "as passrate from (SELECT * ,SUM(pass+fail) as count from (SELECT caseId ,count(case WHEN `caseFlag`=1 then 1 END)  AS pass,"
                                     "count(case WHEN `caseFlag`=0 or caseFlag is null  then 2 END)  AS fail from case_result GROUP BY caseId)m GROUP BY m.caseId )m "
                                     "ORDER BY passrate desc,caseId desc LIMIT 10)n LEFT JOIN testcase on n.caseId = testcase.id")





    top_run = query_util.result_to_dict(res_toprun)
    log.info('caseTop_toprun sql执行结果转换为 json数据为 {}'.format(top_run))
    top_pass = query_util.result_to_dict(res_toppass)
    log.info('caseTop_toprun sql执行结果转换为 json数据为 {}'.format(top_pass))
    if len(top_run) != 0:
        # for i in top_run:
        #     passrate = i['passcount'] / i['count'] * 100
        #     passrate = round(passrate, 1)
        #     d = {'passrate': passrate}
        #     i.update(d)
        # top_rate = sorted(top_run, key=lambda x: x['passrate'], reverse=True)

        return top_run, top_pass
    else:
        log.info('查询的结果为空')
        return 1


def get_project_data(project_id):
    # 获取项目执行总数

    total = db.session.execute("SELECT COUNT(*) as a from (SELECT testcase.projects_id ,case_result.caseId,"
                               "case_result.caseFlag from testcase LEFT JOIN case_result on "
                               "testcase.id = case_result.caseId)m WHERE m.projects_id= " + str(project_id))
    total = query_util.result_to_dict(total)
    try:
        total = total[0]['a']
    except Exception:
        total = 0

    success_total = db.session.execute("SELECT COUNT(*) as a from (SELECT testcase.projects_id ,"
                                       "case_result.caseId,"
                                       "case_result.caseFlag from testcase LEFT JOIN case_result on "
                                       "testcase.id = case_result.caseId)m WHERE m.caseFlag= 1 and m.projects_id= " +
                                       str(project_id))
    success_total = query_util.result_to_dict(success_total)
    try:
        success_total = success_total[0]['a']
    except Exception:
        success_total = 0
    # 当前项目最新的task执行结果
    current_success_rate = db.session.execute(text("SELECT successTotal,failTotal,total,passRate from (SELECT * from "
                                                   "home_view WHERE projectId = :pid ORDER BY createtime DESC LIMIT "
                                                   "10000) n  GROUP BY n.projectId"), {'pid': project_id})
    current_success_rate = query_util.result_to_dict(current_success_rate)
    try:
        current_success_rate = current_success_rate[0]
    except Exception:
        current_success_rate = {"failTotal": 0, "passRate": "0.0", "successTotal": 0, "total": 0}
    #  获取近七次的执行结果
    day_execute = db.session.execute(text("SELECT successTotal as success,failTotal as fail,total as total,"
                                          "UNIX_TIMESTAMP(createtime)*1000 as create_time FROM "
                                          "(SELECT * from home_view WHERE projectId=:pid ORDER BY "
                                          "createtime desc LIMIT 7)m ORDER BY m.createtime ASC"), {'pid': project_id})
    day_execute = query_util.result_to_dict(day_execute)

    sevenCases = db.session.execute(text("select count(*) as count from testcase  where DATE_SUB(CURDATE(), "
                                         "INTERVAL 7 DAY) <= date(create_at) and projects_id=:pid"),
                                    {'pid': project_id})
    sevenCases = query_util.result_to_dict(sevenCases)
    try:
        sevenCases = sevenCases[0]['count']
    except Exception:
        sevenCases = 0
    return {
        'execute_total': total,
        'success_total': success_total,
        'sevenCases': sevenCases,
        'current_success_rate': current_success_rate,
        'day_execute': day_execute,

    }


if __name__ == '__main__':
    res =today()
    print(res)
