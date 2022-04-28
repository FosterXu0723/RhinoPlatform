"""
@File: views.py
@author: guoweiliang
@date: 2021/5/10
"""
import traceback
from datetime import datetime, timedelta
from typing import List

from apscheduler.triggers.cron import CronTrigger
from flask import request, jsonify, g
from sqlalchemy import and_

from app import db
from app import scheduler
from app.models import Task, Testcase
from app.users.auth import auth_token
from common.Log import log
from core.ci.MatchCase import matchApi, matchCase
from . import task
from .apscheduler_listner import MyTrigger
from .tasks import taskCase


@task.route("/addTask", methods=["post"])
@auth_token.login_required
def addTask():
    """
    添加一个date/类interval型任务
    根据项目或者testcase来关联到具体某一个job
    trigger type支持 cron,data, interval
    trigger==cron=> taskId，runtime：list(day_of_week,hour,minute,second)
    trigger==data => taskId,runTime
        run_date (datetime|str) – the date/time to run the job at
        timezone (datetime.tzinfo|str) – time zone for run_date if it doesn’t have one already
    trigger==interval => weeks, days, hours, minutes, seconds, start_date
        weeks (int) – number of weeks to wait
        days (int) – number of days to wait
        hours (int) – number of hours to wait
        minutes (int) – number of minutes to wait
        seconds (int) – number of seconds to wait
        start_date (datetime|str) – starting point for the interval calculation
    """
    requestForm = request.form
    jobName: str = requestForm.get("taskName")
    jobProject = requestForm.get("projectId") or None
    # jobProjectList = jobProject.split(",")
    taskType = requestForm.get("taskType")
    runDate = requestForm.get("runDate")
    runTime = requestForm.get("runTime")
    regularType = requestForm.get("taskRegularType")  # 支持三种类型weeks,days,hours
    regularNumber = requestForm.get("taskRegularNum")
    # 任务名称不允许重复
    if Task.query.filter(and_(Task.task_name == jobName.strip()), Task.task_status == True).first():
        return jsonify({
            "code": 99999,
            "msg": "已经存在相同名称的任务，请修改名称后保存！"
        })

    if taskType == "date":
        runtime = runDate + " " + runTime
        try:
            scheduler.add_job(id=jobName, func=taskCase, trigger="date", run_date=runtime, replace_existing=True,
                              misfire_grace_time=3600,
                              kwargs={"projectId": jobProject, "taskName": jobName})

        except Exception as e:
            log.error("请求出错：", str(traceback.format_exc()))
            return jsonify({
                "code": 99999,
                "msg": "新增任务失败,{}".format(e)
            })

    elif taskType == "interval":
        try:
            """
            scheduler.add_job 此时是将job写入内存中，暂时未存入apscheduler自动生成的job表中，此时获取直接获取对象的next_run_time失败
            """

            if regularType == "weeks":
                scheduler.add_job(id=jobName, func=taskCase, trigger="interval", weeks=int(regularNumber),
                                  misfire_grace_time=3600,
                                  replace_existing=True, kwargs={"projectId": jobProject, "taskName": jobName})

            elif regularType == "days":
                scheduler.add_job(id=jobName, func=taskCase, trigger="interval", days=int(regularNumber),
                                  misfire_grace_time=3600,
                                  replace_existing=True, kwargs={"projectId": jobProject, "taskName": jobName})

            else:  # 类型是hours
                scheduler.add_job(id=jobName, func=taskCase, trigger="interval", hours=int(regularNumber),
                                  misfire_grace_time=3600,
                                  replace_existing=True, kwargs={"projectId": jobProject, "taskName": jobName})

        except Exception as e:
            log.error("请求出错：", str(traceback.format_exc()))
            return jsonify({
                "code": 99999,
                "msg": "新增任务失败,{}".format(e)
            })
    else:  # task type是corn
        cron = requestForm.get("cronConfig")
        try:
            scheduler.add_job(id=jobName, func=taskCase, trigger=MyTrigger.from_crontab(cron),
                              replace_existing=True, misfire_grace_time=3600,
                              kwargs={"projectId": jobProject, "taskName": jobName})
        except Exception as e:
            log.error("请求出错：", str(traceback.format_exc()))
            return jsonify({
                "code": 99999,
                "msg": "新增任务失败,{}".format(e)
            })
    # 写入task

    task = Task(task_name=jobName, owner=g.flask_httpauth_user.get('id'), task_type=taskType, create_at=datetime.now(),
                task_start=scheduler.get_job(jobName).next_run_time)

    # 获取项目cases
    cases: List = Testcase.query.filter(and_(Testcase.projects_id == int(jobProject)),
                                        Testcase.open_status == True).all()
    for case in cases:
        task.task_cases.append(case)

    db.session.add(task)
    db.session.commit()
    return jsonify({
        "code": 10000,
        "msg": "add task success, next runtime at {}".format(scheduler.get_job(jobName).next_run_time),
    })


@task.route("/pause", methods=["post"])
def pauseTask():
    """
    暂停定时任务
    :return:
    """
    try:
        taskId = request.form.get("taskId")
        task: Task = Task.query.filter(Task.id == taskId).first()
        if task.task_type == "date":  # 不需要暂停
            return jsonify({
                "code": 99999,
                "msg": "已经执行完成的任务不能够暂停！"
            })
        task.task_status = not task.task_status
        db.session.add(task)
        db.session.commit()
        # taskName 对应scheduler的taskId
        scheduler.pause_job(task.task_name)
        return jsonify({
            "code": 10000,
            "msg": f"job: {task.task_name} paused success" if not task.task_status else f"job: {task.task_name} resume success"
        })
    except Exception as e:
        return jsonify({
            "code": 99999,
            "smg": "暂停任务失败{}".format(str(traceback.format_exc(e)))
        })


@task.route("/resume", methods=["post"])
def resumeTask():
    """
    恢复定时任务
    :return:
    """
    taskName = request.form.get("taskName")
    try:
        scheduler.resume_job(taskName)
        return jsonify({
            "code": 10000,
            "msg": f"job {taskName} resume success,next run time {scheduler.get_job(taskName).next_run_time}"
        })
    except Exception as e:
        return jsonify({
            "code": 99999,
            "msg": "job {} resume failed, {}".format(taskName, str(traceback.format_exc()))
        })


@task.route("/remove", methods=["post"])
def removeTask():
    """
    删除定时任务
    :return:
    """
    taskName = request.form.get("taskName")
    try:
        scheduler.remove_job(taskName)
        return jsonify({
            "code": 10000,
            "msg": "job {} removed success".format(taskName)
        })
    except Exception as e:
        return jsonify({
            "code": 99999,
            "msg": "job {} removed failed.{}".format(taskName, str(traceback.format_exc()))
        })


@task.route("/edit", methods=['post'])
def fixTask():
    """
    编辑定时任务
    :return:
    """
    requestData = request.form
    taskId = int(requestData.get("taskId"))
    jobName: str = requestData.get("taskName")  # 不允许修改
    jobProject = requestData.get("projectId") or None
    taskType = requestData.get("taskType")  # 不予许修改
    runDate = requestData.get("runDate")
    runTime = requestData.get("runTime")
    regularType = requestData.get("taskRegularType")  # 支持三种类型weeks,days,hours
    regularNumber = requestData.get("taskRegularNum")
    task = Task.query.filter(Task.id == taskId).first()

    if taskType == "date":
        runtime = runDate + " " + runTime  # 拼接时间
        try:
            scheduler.modify_job(id=jobName, trigger="date", run_date=runtime)
            if task:
                # 仅需要更改执行时间
                task.task_start = scheduler.get_job(jobName).next_run_time
                task.update_at = datetime.now()
                try:
                    db.session.add(task)
                    db.session.commit()
                    return jsonify({
                        "code": 10000,
                        "msg": "编辑成功"
                    })
                except Exception as e:
                    db.session.rollback()
                    return jsonify({
                        "code": 99999,
                        "msg": "编辑任务失败:{}".format(e)
                    })
        except Exception as e:
            log.error("【编辑任务】失败：{}".format(str(traceback.format_exc())))
            return jsonify({
                "code": 99999,
                "msg": "编辑任务失败:{}".format(e)
            })

    else:  # 表示是interval

        if regularType == "weeks":
            try:
                scheduler.modify_job(id=jobName, trigger="interval", weeks=int(regularNumber))
                task.task_start = scheduler.get_job(jobName).next_run_time
                task.update_at = datetime.now()
                db.session.add(task)
                db.session.commit()
                return jsonify({
                    "code": 10000,
                    "msg": "编辑成功"
                })
            except Exception as e:
                log.error('【编辑任务】失败:{}'.format(str(traceback.format_exc())))
                return jsonify({
                    "code": 99999,
                    "msg": "编辑任务失败:{}".format(e)
                })

        elif regularType == "days":
            try:
                scheduler.modify_job(id=jobName, trigger="interval", days=int(regularNumber))
                task.task_start = scheduler.get_job(jobName).next_run_time
                task.update_at = datetime.now()
                db.session.add(task)
                db.session.commit()
                return jsonify({
                    "code": 10000,
                    "msg": "编辑成功"
                })
            except Exception as e:
                log.error('【编辑任务】失败:{}'.format(e))
                return jsonify({
                    "code": 99999,
                    "msg": "编辑任务失败:{}".format(e)
                })

        else:  # interval的类型是hours
            try:
                scheduler.modify_job(id=jobName, trigger="interval", hours=int(regularNumber))
                task.task_start = scheduler.get_job(jobName).next_run_time
                task.update_at = datetime.now()
                db.session.add(task)
                db.session.commit()
                return jsonify({
                    "code": 10000,
                    "msg": "编辑成功"
                })
            except Exception as e:
                log.error('【编辑任务】失败:{}'.format(str(traceback.format_exc())))
                return jsonify({
                    "code": 99999,
                    "msg": "编辑任务失败:{}".format(e)
                })


@task.route("/list", methods=['get'])
def taskList():
    """
    分页请求任务列表
    :return:
    """
    page = int(request.args.get("page"))
    pageSize = int(request.args.get("pageSize"))
    tasks = Task.query.filter().order_by(Task.id.desc()).paginate(page=page, per_page=pageSize)
    if len(tasks.items) > 0:
        return jsonify({
            "code": 10000,
            "msg": "success",
            "data": {
                "list": list(map(lambda x: x.to_dict(), tasks.items)),
                "total": tasks.total
            }
        })
    else:
        return jsonify({
            "code": 99999,
            "msg": "暂无定时任务！",
            "data": None
        })


@task.route("/gitlab_hook", methods=["post"])
def gitlabHook():
    data = eval(request.get_data().decode())
    projectName = data.get("project")
    caseIds = matchCase(matchApi(projectName))
    if len(caseIds) == 0:
        return jsonify({
            'code': 99999,
            'msg': '当前应用没有关联case'
        })
    log.info(f"获取到 {projectName} 工程相关联case{caseIds}")
    taskName = projectName + datetime.now().strftime("%Y%m%d%H%M")
    # 外层的flask应用已经启动scheduler，这边不再次启动scheduler的时候，会被scheduler底层认为当前是stop状态，导致job无法正常录入
    # if self.state == STATE_STOPPED:   所以这边手动启动一下

    scheduler.add_job(id=taskName, func=taskCase, trigger="date",
                      run_date=(datetime.now() + timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S"),
                      replace_existing=True, misfire_grace_time=3600, coalesce=True,
                      kwargs={"caseIds": caseIds, "taskName": taskName})
    task = Task(task_name=taskName, task_type="date", task_start=scheduler.get_job(taskName).next_run_time,
                create_at=datetime.now())
    try:
        db.session.add(task)
        db.session.commit()
        return jsonify({
            "code": 10000,
            "msg": "success"
        })
    except:
        db.session.rollback()
        return jsonify({
            "code": 99999,
            "msg": "failed"
        })
