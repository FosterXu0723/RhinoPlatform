"""
@File:views.py
@author:zhanfei
@date: 2021/03/31
"""

import os
import json
import traceback
from datetime import datetime
import xlrd
import base64

from flask_mail import Mail, Message
from ast import literal_eval
from flask import request, Flask, jsonify, send_from_directory, make_response, Response, send_file, render_template
from werkzeug.utils import secure_filename

from common.Log import log
from . import publishmanage

from config import ProdConfig
from app.utils import notEmpty
from app.models import PublishManage
from app.models import PublishManage_AfterEndDetails
from app.models import PublishManage_FrontEndDetails
from app import db, mail
from app.users.auth import auth_token
from sqlalchemy import or_, and_
from config import Config

# 本地环境地址
# UPLOAD_FOLDER1=r'../../../upload/publishmanage/afterReport'
# UPLOAD_FOLDER2=r'../../../upload/publishmanage/afterImageTask'
# UPLOAD_FOLDER3=r'../../../upload/publishmanage/frontReport'
# UPLOAD_FOLDER4=r'../../../upload/publishmanage/frontImageTask'
# 线上环境地址
UPLOAD_FOLDER1 = r'/home/pyproject/upload/publishmanage/afterReport'
UPLOAD_FOLDER2 = r'/home/pyproject/upload/publishmanage/afterImageTask'
UPLOAD_FOLDER3 = r'/home/pyproject/upload/publishmanage/frontReport'
UPLOAD_FOLDER4 = r'/home/pyproject/upload/publishmanage/frontImageTask'
basedir = os.path.abspath(os.path.dirname(__file__))

ALLOWED_EXTENSIONS1 = ('xls', 'xlsx')
ALLOWED_EXTENSIONS2 = ('jpg', 'jpeg', 'png')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS1


def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS2


@publishmanage.route('/publishmanage/afterEnd/uploadreport', methods=['POST'])
# @auth_token.login_required
def afterEndUploadReport():
    """
    后端发布上传测试报告接口
    """
    file_dir = os.path.join(ProdConfig.UPLOAD_FOLDER1)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['file']
    taskDevelopment = request.form.get("taskDevelopment")
    taskBusiness = request.form.get("taskBusiness")
    taskDate = datetime.strptime(request.form.get("publishDate"), '%Y%m%d').strftime('%Y-%m-%d')
    taskName = request.form.get("publishDate") + request.form.get("taskBusiness") + request.form.get(
        "taskDevelopment") + "发布项目"
    taskStatus = request.form.get("taskStatus")
    taskAuthor = request.form.get("taskAuthor")

    '''------------此部分内容是获取excel报告中的需求名称-------'''
    file_data = f.read()
    workbook = xlrd.open_workbook(file_contents=file_data)
    table = workbook.sheet_by_index(0)
    requireName = str(table.col_values(0, 2)).replace("&","和")
    afterDeveloper = str(table.col_values(7, 2))
    '''-------------------------------------------------------'''

    '''------------文件指针重新从文件头开始------------------'''
    f.seek(0)
    '''-------------------------------------------------------'''

    if f and allowed_file(f.filename):
        fname = secure_filename(f.filename)
        f.save(os.path.join(file_dir, fname))
        task_names = PublishManage.query.with_entities(PublishManage.task_name).filter_by(delete_id=0).all()
        for task_name in task_names:
            if taskName == task_name[0]:
                return jsonify({
                    'code': 99998,
                    'msg': "发布任务名称已存在!"
                })
        tasks = PublishManage(task_development=taskDevelopment, task_name=taskName, task_business=taskBusiness,
                              task_author=taskAuthor, testreport_url=file_dir, testreport_realname=fname,
                              task_date=taskDate, task_status=taskStatus, require_name=requireName)
        try:
            db.session.add(tasks)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'code': 99999,
                "msg": "提交数据失败!"
            })
        for requireName, afterDeveloper in zip(eval(requireName), eval(afterDeveloper)):
            if len(afterDeveloper) != 0 and (afterDeveloper != '无'):
                afterDeveloper1 = '[]'
                afterDeveloper1 = str(afterDeveloper.split('+'))
                taskID = PublishManage.query.with_entities(PublishManage.id).filter(PublishManage.delete_id == 0,
                                                                                    PublishManage.task_name == taskName).all()
                details = PublishManage_AfterEndDetails(task_id=taskID[0][0], require_name=requireName,
                                                        after_developer=afterDeveloper1, publish_project='[]',
                                                        publish_branch='', jar_name='[]', check_sql='',
                                                        other_require='')
                try:
                    db.session.add(details)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return jsonify({
                        'code': 99999,
                        "msg": "提交数据失败!"
                    })
        return jsonify({
            'code': 10000,
            'msg': "提交数据成功!"
        })
    else:
        return jsonify({
            'code': 99999,
            'msg': "提交数据失败!"
        })


@publishmanage.route('/publishmanage/frontEnd/uploadreport', methods=['POST'])
# @auth_token.login_required
def frontEndUploadReport():
    """
    前端上传测试报告接口
    """
    try:
        file_dir = os.path.join(ProdConfig.UPLOAD_FOLDER3)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        f = request.files['file']
        taskDevelopment = request.form.get("taskDevelopment")
        taskBusiness = request.form.get("taskBusiness")
        taskDate = datetime.strptime(request.form.get("publishDate"), '%Y%m%d').strftime('%Y-%m-%d')
        taskName = request.form.get("publishDate") + request.form.get("taskBusiness") + request.form.get(
            "taskDevelopment") + "发布项目"
        taskStatus = request.form.get("taskStatus")
        taskAuthor = request.form.get("taskAuthor")

        '''------------此部分内容是获取excel报告中的需求名称-------'''
        file_data = f.read()
        workbook = xlrd.open_workbook(file_contents=file_data)
        table = workbook.sheet_by_index(0)
        requireName = str(table.col_values(0, 2)).replace("&","和")
        frontDeveloper = str(table.col_values(6, 2))
        '''-------------------------------------------------------'''

        '''------------文件指针重新从文件头开始------------------'''
        f.seek(0)
        '''-------------------------------------------------------'''

        if f and allowed_file(f.filename):
            fname = secure_filename(f.filename)
            f.save(os.path.join(file_dir, fname))
            task_names = PublishManage.query.with_entities(PublishManage.task_name).filter_by(delete_id=0).all()
            for task_name in task_names:
                if taskName == task_name[0]:
                    return jsonify({
                        'code': 99998,
                        'msg': "发布任务名称已存在!"
                    })
            tasks = PublishManage(task_development=taskDevelopment, task_name=taskName, task_business=taskBusiness,
                                  task_author=taskAuthor, testreport_url=file_dir, testreport_realname=fname,
                                  task_date=taskDate, task_status=taskStatus, require_name=requireName)
            try:
                db.session.add(tasks)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'code': 99999,
                    "msg": "提交数据失败!"
                })
            for requireName, frontDeveloper in zip(eval(requireName), eval(frontDeveloper)):
                if len(frontDeveloper) != 0 and (frontDeveloper != '无'):
                    frontDeveloper1 = '[]'
                    frontDeveloper1 = str(frontDeveloper.split('+'))
                    taskID = PublishManage.query.with_entities(PublishManage.id).filter(PublishManage.delete_id == 0,
                                                                                        PublishManage.task_name == taskName).all()
                    details = PublishManage_FrontEndDetails(task_id=taskID[0][0], require_name=requireName,
                                                            front_developer=frontDeveloper1, publish_project='[]',
                                                            publish_branch='', app_renew='', other_require='')
                    try:
                        db.session.add(details)
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        return jsonify({
                            'code': 99999,
                            "msg": "提交数据失败!"
                        })
            return jsonify({
                'code': 10000,
                'msg': "提交数据成功!"
            })
        else:
            return jsonify({
                'code': 99999,
                'msg': "提交数据失败!"
            })
    except Exception as e:
        log.error("请求出现报错:{}".format(e))


@publishmanage.route('/publishmanage/afterEnd/tasksList', methods=['POST'])
# @auth_token.login_required
def afterEndTasksList():
    """
    后端已创建的发布任务列表接口
    """
    data = []
    requestParams = request.form
    taskName = requestParams.get('taskName')
    taskAuthor = requestParams.get('taskAuthor')
    taskStatus = requestParams.get('taskStatus')
    page = int((requestParams.get('page')))
    pageSize = int(requestParams.get('pageSize'))
    if taskName != '' and taskAuthor != '' and taskStatus != '':
        filters = {and_(
            and_(PublishManage.task_name.like("%" + taskName + "%"), PublishManage.task_author == taskAuthor,
                 PublishManage.task_status == taskStatus, PublishManage.task_development == '后端'),
            PublishManage.delete_id == 0)}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})

    elif taskName == '' and taskAuthor != '' and taskStatus != '':
        filters = {and_(and_(PublishManage.task_author == taskAuthor, PublishManage.task_status == taskStatus,
                             PublishManage.task_development == '后端'), PublishManage.delete_id == 0)}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})



    elif taskName != '' and taskAuthor != '' and taskStatus == '':
        filters = {and_(
            and_(PublishManage.task_name.like("%" + taskName + "%"), PublishManage.task_author == taskAuthor,
                 PublishManage.task_development == '后端'), PublishManage.delete_id == 0)}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})


    elif taskName != '' and taskAuthor == '' and taskStatus != '':
        filters = {and_(
            and_(PublishManage.task_name.like("%" + taskName + "%"), PublishManage.task_status == taskStatus,
                 PublishManage.task_development == '后端'), PublishManage.delete_id == 0)}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})


    elif taskName != '' and taskAuthor == '' and taskStatus == '':
        filters = {and_(PublishManage.task_name.like("%" + taskName + "%"), PublishManage.delete_id == 0,
                        PublishManage.task_development == '后端')}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})

    elif taskName == '' and taskAuthor != '' and taskStatus == '':
        filters = {and_(PublishManage.task_author == taskAuthor, PublishManage.delete_id == 0,
                        PublishManage.task_development == '后端')}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})

    elif taskName == '' and taskAuthor == '' and taskStatus != '':
        filters = {and_(PublishManage.task_status == taskStatus, PublishManage.delete_id == 0,
                        PublishManage.task_development == '后端')}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})

    else:
        filters = {and_(or_(PublishManage.task_name.like("%" + taskName + "%"), PublishManage.task_author == taskAuthor,
                            PublishManage.task_status == taskStatus), PublishManage.delete_id == 0,
                        PublishManage.task_development == '后端')}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})


@publishmanage.route('/publishmanage/frontEnd/tasksList', methods=['POST'])
# @auth_token.login_required
def frontEndTasksList():
    """
    前端已创建的发布任务列表接口
    """
    data = []
    requestParams = request.form
    taskName = requestParams.get('taskName')
    taskAuthor = requestParams.get('taskAuthor')
    taskStatus = requestParams.get('taskStatus')
    page = int((requestParams.get('page')))
    pageSize = int(requestParams.get('pageSize'))
    if taskName != '' and taskAuthor != '' and taskStatus != '':
        filters = {and_(
            and_(PublishManage.task_name.like("%" + taskName + "%"), PublishManage.task_author == taskAuthor,
                 PublishManage.task_status == taskStatus, PublishManage.task_development == '前端'),
            PublishManage.delete_id == 0)}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})

    elif taskName == '' and taskAuthor != '' and taskStatus != '':
        filters = {and_(and_(PublishManage.task_author == taskAuthor, PublishManage.task_status == taskStatus,
                             PublishManage.task_development == '前端'), PublishManage.delete_id == 0)}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})



    elif taskName != '' and taskAuthor != '' and taskStatus == '':
        filters = {and_(
            and_(PublishManage.task_name.like("%" + taskName + "%"), PublishManage.task_author == taskAuthor,
                 PublishManage.task_development == '前端'), PublishManage.delete_id == 0)}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})


    elif taskName != '' and taskAuthor == '' and taskStatus != '':
        filters = {and_(
            and_(PublishManage.task_name.like("%" + taskName + "%"), PublishManage.task_status == taskStatus,
                 PublishManage.task_development == '前端'), PublishManage.delete_id == 0)}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})


    elif taskName != '' and taskAuthor == '' and taskStatus == '':
        filters = {and_(PublishManage.task_name.like("%" + taskName + "%"), PublishManage.delete_id == 0,
                        PublishManage.task_development == '前端')}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})

    elif taskName == '' and taskAuthor != '' and taskStatus == '':
        filters = {and_(PublishManage.task_author == taskAuthor, PublishManage.delete_id == 0,
                        PublishManage.task_development == '前端')}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})

    elif taskName == '' and taskAuthor == '' and taskStatus != '':
        filters = {and_(PublishManage.task_status == taskStatus, PublishManage.delete_id == 0,
                        PublishManage.task_development == '前端')}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})

    else:
        filters = {and_(or_(PublishManage.task_name.like("%" + taskName + "%"), PublishManage.task_author == taskAuthor,
                            PublishManage.task_status == taskStatus), PublishManage.delete_id == 0,
                        PublishManage.task_development == '前端')}
        filedatas = PublishManage.query.filter(*filters).order_by(db.desc(PublishManage.task_date)).offset(
            (page - 1) * pageSize).limit(pageSize).all()
        totaldatas = PublishManage.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code': 10000, 'msg': 'Success', 'data': data, 'total': 0})
        else:
            for filedata in filedatas:
                data.append({'taskBusiness': filedata.task_business, 'taskName': filedata.task_name,
                             'fileName': filedata.testreport_realname, 'taskAuthor': filedata.task_author,
                             'taskDate': str(filedata.task_date), 'taskStatus': filedata.task_status})
            return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totaldatas})


@publishmanage.route('/publishmanage/afterEnd/deleteTask', methods=['POST'])
# @auth_token.login_required
def afterEndDeleteTask():
    """
    后端删除列表中的发布数据接口
    """
    requestParams = request.form
    taskName = requestParams.get('taskName')
    if taskName != '':
        details = PublishManage_AfterEndDetails.query.filter(PublishManage.delete_id == 0,
                                                             PublishManage.task_name == taskName,
                                                             PublishManage.id == PublishManage_AfterEndDetails.task_id).delete(
            synchronize_session=False)
        task = PublishManage.query.filter_by(task_name=taskName).update({"delete_id": 1})
        try:
            db.session.commit()
            return jsonify({
                'code': 10000,
                'msg': "删除数据成功!"
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'code': 99999,
                "msg": "删除数据失败!"
            })
    else:
        return jsonify({
            'code': 99999,
            'msg': "删除数据失败!"
        })


@publishmanage.route('/publishmanage/frontEnd/deleteTask', methods=['POST'])
# @auth_token.login_required
def frontEndDeleteTask():
    """
    前端删除列表中的发布数据接口
    """
    requestParams = request.form
    taskName = requestParams.get('taskName')
    if taskName != '':
        details = PublishManage_FrontEndDetails.query.filter(PublishManage.delete_id == 0,
                                                             PublishManage.task_name == taskName,
                                                             PublishManage.id == PublishManage_FrontEndDetails.task_id).delete(
            synchronize_session=False)
        task = PublishManage.query.filter_by(task_name=taskName).update({"delete_id": 1})
        try:
            db.session.commit()
            return jsonify({
                'code': 10000,
                'msg': "删除数据成功!"
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'code': 99999,
                "msg": "删除数据失败!"
            })
    else:
        return jsonify({
            'code': 99999,
            'msg': "删除数据失败!"
        })


@publishmanage.route('/publishmanage/afterEnd/downLoadTask', methods=['POST'])
# @auth_token.login_required
def afterEndDownLoadTask():
    """
    后端下载测试报告接口
    """
    requestParams = request.form
    taskName = requestParams.get('taskName')
    fileName = requestParams.get('fileName')
    db_taskurl = PublishManage.query.with_entities(PublishManage.testreport_url).filter_by(testreport_realname=fileName,
                                                                                           task_name=taskName,
                                                                                           delete_id=0).all()
    db_reportrealname = PublishManage.query.with_entities(PublishManage.testreport_realname).filter_by(
        testreport_realname=fileName, task_name=taskName, delete_id=0).all()
    root_path = str(db_taskurl[0][0])
    src_name = str(db_reportrealname[0][0])
    upload_path = os.path.join(root_path, src_name)
    if os.path.isfile(upload_path):
        response = send_from_directory(root_path, src_name, as_attachment=True)
        response.headers["Content-Type"] = "application/octet-stream"
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        # response.headers["Content-Disposition"]="attachment;filename={};".format(src_name)
        # print('response:',response)
        return response
    else:
        return jsonify({
            'code': 99999,
            'msg': "下载失败!"
        })


@publishmanage.route('/publishmanage/frontEnd/downLoadTask', methods=['POST'])
# @auth_token.login_required
def frontEndDownLoadTask():
    """
    前端下载测试报告接口
    """
    requestParams = request.form
    taskName = requestParams.get('taskName')
    fileName = requestParams.get('fileName')
    db_taskurl = PublishManage.query.with_entities(PublishManage.testreport_url).filter_by(testreport_realname=fileName,
                                                                                           task_name=taskName,
                                                                                           delete_id=0).all()
    db_reportrealname = PublishManage.query.with_entities(PublishManage.testreport_realname).filter_by(
        testreport_realname=fileName, task_name=taskName, delete_id=0).all()
    root_path = str(db_taskurl[0][0])
    src_name = str(db_reportrealname[0][0])
    upload_path = os.path.join(root_path, src_name)
    if os.path.isfile(upload_path):
        response = send_from_directory(root_path, src_name, as_attachment=True)
        response.headers["Content-Type"] = "application/octet-stream"
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        # response.headers["Content-Disposition"]="attachment;filename={};".format(src_name)
        # print('response:',response)
        return response
    else:
        return jsonify({
            'code': 99999,
            'msg': "下载失败!"
        })


@publishmanage.route('/publishmanage/afterEnd/taskDetails', methods=['POST'])
# @auth_token.login_required
def afterEndTaskDetails():
    """
    后端发布任务详情接口
    """
    data = []
    requestParams = request.form
    taskName = requestParams.get('taskName')
    details = PublishManage_AfterEndDetails.query.filter(PublishManage.delete_id == 0,
                                                         PublishManage.task_name == taskName,
                                                         PublishManage.id == PublishManage_AfterEndDetails.task_id).all()
    if len(details) == 0:
        return jsonify({'code': 10001, 'msg': '未查询到数据!', 'data': data})
    else:
        for detail in details:
            data.append({'requireId': detail.id, 'requireName': detail.require_name,
                         'afterDeveloper': eval(detail.after_developer), 'publishProject': eval(detail.publish_project),
                         'branch': detail.publish_branch, 'jarPackage': eval(detail.jar_name),
                         'checkSQL': detail.check_sql, 'remarks': detail.other_require})
        return jsonify({'code': 10000, 'msg': 'success', 'data': data})


@publishmanage.route('/publishmanage/frontEnd/taskDetails', methods=['POST'])
# @auth_token.login_required
def frontEndTaskDetails():
    """
    前端发布任务详情接口
    """
    data = []
    requestParams = request.form
    taskName = requestParams.get('taskName')
    details = PublishManage_FrontEndDetails.query.filter(PublishManage.delete_id == 0,
                                                         PublishManage.task_name == taskName,
                                                         PublishManage.id == PublishManage_FrontEndDetails.task_id).all()
    if len(details) == 0:
        return jsonify({'code': 10001, 'msg': '未查询到数据!', 'data': data})
    else:
        for detail in details:
            data.append({'requireId': detail.id, 'requireName': detail.require_name,
                         'frontDeveloper': eval(detail.front_developer), 'publishProject': eval(detail.publish_project),
                         'branch': detail.publish_branch, 'appRenew': detail.app_renew,
                         'remarks': detail.other_require})
        return jsonify({'code': 10000, 'msg': 'success', 'data': data})


@publishmanage.route('/publishmanage/afterEnd/saveTask', methods=['POST'])
# @auth_token.login_required
def afterEndSaveTask():
    """
    编辑后端发布数据接口
    """
    """
    ImmutableMultiDict转为dict取key
    """
    try:
        for key in request.form.to_dict().keys():
            requestParams = eval(key)

        """
        取列表中的每个数据也就是前端表格中的每一条数据
        """
        # requestParams=request.form
        if requestParams['detailsData'] != '':
            taskName = requestParams['taskName']
            requireName = requestParams['detailsData']['requireName']
            """
            查询发布管理详情表中是否存在已经建立的发布详情数据
            """
            taskID = PublishManage.query.with_entities(PublishManage.id).filter(PublishManage.delete_id == 0,
                                                                                PublishManage.task_name == taskName).all()
            taskIDS = PublishManage_AfterEndDetails.query.with_entities(PublishManage_AfterEndDetails.task_id).filter(
                PublishManage.delete_id == 0, PublishManage.task_name == taskName,
                PublishManage.id == PublishManage_AfterEndDetails.task_id).all()
            requireNames = PublishManage_AfterEndDetails.query.with_entities(
                PublishManage_AfterEndDetails.require_name).filter(PublishManage.delete_id == 0,
                                                                   PublishManage.task_name == taskName,
                                                                   PublishManage.id == PublishManage_AfterEndDetails.task_id,
                                                                   PublishManage_AfterEndDetails.require_name == requireName).all()

            # 先判断提交的字段是否为空
            if requestParams['taskName'] != '' and requestParams['detailsData']['requireName'] != '' and len(
                    requestParams['detailsData']['afterDeveloper']) != 0 and len(
                    requestParams['detailsData']['publishProject']) != 0 and requestParams['detailsData'][
                'branch'] != '' and len(requestParams['detailsData']['jarPackage']) != 0 and \
                    requestParams['detailsData']['checkSQL'] != '':

                # 如果保存的需求在发布详情表中不存在,直接插入数据
                if len(requireNames) == 0:
                    taskDetails = requestParams['detailsData']
                    details = PublishManage_AfterEndDetails(task_id=taskID[0][0],
                                                            require_name=str(taskDetails['requireName']),
                                                            after_developer=str(taskDetails['afterDeveloper']),
                                                            publish_project=str(taskDetails['publishProject']),
                                                            publish_branch=str(taskDetails['branch']),
                                                            jar_name=str(taskDetails['jarPackage']),
                                                            check_sql=str(taskDetails['checkSQL']),
                                                            other_require=str(taskDetails['remarks']))
                    try:
                        db.session.add(details)
                        db.session.commit()
                        return jsonify({'code': 10000, 'msg': '数据处理完成!'})
                    except Exception as e:
                        db.session.rollback()
                        return jsonify({'code': 99999, 'msg': '数据处理失败!'})

                # 如果保存的需求在发布详情表中存在,直接更新
                else:
                    taskDetails = requestParams['detailsData']
                    details = PublishManage_AfterEndDetails.query.filter(PublishManage.delete_id == 0,
                                                                         PublishManage.task_name == taskName,
                                                                         PublishManage.id == PublishManage_AfterEndDetails.task_id,
                                                                         PublishManage_AfterEndDetails.require_name == requireName).update(
                        {"require_name": taskDetails['requireName'],
                         "after_developer": str(taskDetails['afterDeveloper']),
                         "publish_project": str(taskDetails['publishProject']), "publish_branch": taskDetails['branch'],
                         "jar_name": str(taskDetails['jarPackage']), "check_sql": taskDetails['checkSQL'],
                         "other_require": taskDetails['remarks']}, synchronize_session=False)
                    try:
                        db.session.commit()
                        return jsonify({'code': 10000, 'msg': '数据处理完成!'})
                    except Exception as e:
                        db.session.rollback()
                        return jsonify({'code': 99999, 'msg': '数据处理失败!'})
            else:
                return jsonify({'code': 99998, 'msg': '有必填项未填!'})

        else:
            return jsonify({'code': 99999, 'msg': '数据处理失败!'})
    except Exception as e:
        log.error("接口请求报错：{}".format(e))


@publishmanage.route('/publishmanage/frontEnd/saveTask', methods=['POST'])
# @auth_token.login_required
def frontEndSaveTask():
    """
    编辑前端发布数据接口
    """

    """
    ImmutableMultiDict转为dict取key
    """
    for key in request.form.to_dict().keys():
        requestParams = eval(key)

    """
    取列表中的每个数据也就是前端表格中的每一条数据
    """
    # requestParams=request.form
    if requestParams['detailsData'] != '':
        taskName = requestParams['taskName']
        requireName = requestParams['detailsData']['requireName']
        requireId = requestParams['detailsData']['requireId']
        """
        查询发布管理详情表中是否存在已经建立的发布详情数据
        """
        taskID = PublishManage.query.with_entities(PublishManage.id).filter(PublishManage.delete_id == 0,
                                                                            PublishManage.task_name == taskName).all()
        taskIDS = PublishManage_FrontEndDetails.query.with_entities(PublishManage_FrontEndDetails.task_id).filter(
            PublishManage.delete_id == 0, PublishManage.task_name == taskName,
            PublishManage.id == PublishManage_FrontEndDetails.task_id).all()
        requireIDs = PublishManage_FrontEndDetails.query.with_entities(PublishManage_FrontEndDetails.id).filter(
            PublishManage.delete_id == 0, PublishManage.task_name == taskName,
            PublishManage.id == PublishManage_FrontEndDetails.task_id,
            PublishManage_FrontEndDetails.id == requireId).all()

        # 先判断提交的字段是否为空
        if requestParams['taskName'] != '' and requestParams['detailsData']['requireName'] != '' and len(
                requestParams['detailsData']['frontDeveloper']) != 0 and len(
                requestParams['detailsData']['publishProject']) != 0 and requestParams['detailsData'][
            'branch'] != '' and requestParams['detailsData']['appRenew'] != '':

            # 如果保存的需求在发布详情表中不存在,直接插入数据
            if len(requireIDs) == 0:
                taskDetails = requestParams['detailsData']
                details = PublishManage_FrontEndDetails(task_id=taskID[0][0],
                                                        require_name=str(taskDetails['requireName']),
                                                        front_developer=str(taskDetails['frontDeveloper']),
                                                        publish_project=str(taskDetails['publishProject']),
                                                        publish_branch=str(taskDetails['branch']),
                                                        app_renew=str(taskDetails['appRenew']),
                                                        other_require=str(taskDetails['remarks']))
                try:
                    db.session.add(details)
                    db.session.commit()
                    return jsonify({'code': 10000, 'msg': '数据处理完成!'})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'code': 99999, 'msg': '数据处理失败!'})

            # 如果保存的需求在发布详情表中存在,直接更新
            else:
                taskDetails = requestParams['detailsData']
                details = PublishManage_FrontEndDetails.query.filter(PublishManage.delete_id == 0,
                                                                     PublishManage.task_name == taskName,
                                                                     PublishManage.id == PublishManage_FrontEndDetails.task_id,
                                                                     PublishManage_FrontEndDetails.id == requireId).update(
                    {"require_name": taskDetails['requireName'], "front_developer": str(taskDetails['frontDeveloper']),
                     "publish_project": str(taskDetails['publishProject']), "publish_branch": taskDetails['branch'],
                     "app_renew": taskDetails['appRenew'], "other_require": taskDetails['remarks']},
                    synchronize_session=False)
                try:
                    db.session.commit()
                    return jsonify({'code': 10000, 'msg': '数据处理完成!'})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'code': 99999, 'msg': '数据处理失败!'})
        else:
            return jsonify({'code': 99998, 'msg': '有必填项未填!'})

    else:
        return jsonify({'code': 99999, 'msg': '数据处理失败!'})


@publishmanage.route('/publishmanage/afterEnd/previewTask', methods=['POST'])
# @auth_token.login_required
def afterEndpreviewTask():
    """
    后端发布任务预览接口
    """
    data = []
    projectList = []
    jarList = []
    requestParams = request.form
    taskName = requestParams.get('taskName')
    details = PublishManage_AfterEndDetails.query.filter(PublishManage.delete_id == 0,
                                                         PublishManage.task_name == taskName,
                                                         PublishManage.id == PublishManage_AfterEndDetails.task_id).all()
    projects = PublishManage_AfterEndDetails.query.with_entities(PublishManage_AfterEndDetails.publish_project).filter(
        PublishManage.delete_id == 0, PublishManage.task_name == taskName,
        PublishManage.id == PublishManage_AfterEndDetails.task_id).all()
    for project in projects:
        projectList += (eval(project[0]))
    if '无' in projectList:
        while '无' in projectList:
            projectList.remove('无')
    else:
        projectList = projectList
    jars = PublishManage_AfterEndDetails.query.with_entities(PublishManage_AfterEndDetails.jar_name).filter(
        PublishManage.delete_id == 0, PublishManage.task_name == taskName,
        PublishManage.id == PublishManage_AfterEndDetails.task_id).all()
    for jar in jars:
        jarList += (eval(jar[0]))
    if '无' in jarList:
        while '无' in jarList:
            jarList.remove('无')
    else:
        jarList = jarList
    if len(details) == 0:
        return jsonify({'code': 10000, 'msg': 'Success', 'data': data})
    for detail in details:
        after_developer = ", ".join(eval(detail.after_developer))
        publish_project = ", ".join(eval(detail.publish_project))
        jar_name = ", ".join(eval(detail.jar_name))
        project_total = ", ".join(list(set(projectList)))
        jar_total = ", ".join(list(set(jarList)))
        data.append(
            {'requireName': detail.require_name, 'afterDeveloper': after_developer, 'publishProject': publish_project,
             'branch': detail.publish_branch, 'jarPackage': jar_name, 'checkSQL': detail.check_sql,
             'remarks': detail.other_require, 'projectTotal': project_total, 'jarTotal': jar_total})
    return jsonify({'code': 10000, 'msg': 'success', 'data': data})


@publishmanage.route('/publishmanage/frontEnd/previewTask', methods=['POST'])
# @auth_token.login_required
def frontEndpreviewTask():
    """
    前端发布任务预览接口
    """
    data = []
    projectList = []
    requestParams = request.form
    taskName = requestParams.get('taskName')
    details = PublishManage_FrontEndDetails.query.filter(PublishManage.delete_id == 0,
                                                         PublishManage.task_name == taskName,
                                                         PublishManage.id == PublishManage_FrontEndDetails.task_id).all()
    projects = PublishManage_FrontEndDetails.query.with_entities(PublishManage_FrontEndDetails.publish_project).filter(
        PublishManage.delete_id == 0, PublishManage.task_name == taskName,
        PublishManage.id == PublishManage_FrontEndDetails.task_id).all()
    for project in projects:
        projectList += (eval(project[0]))
    if '无' in projectList:
        while '无' in projectList:
            projectList.remove('无')
    else:
        projectList = projectList
    if len(details) == 0:
        return jsonify({'code': 10000, 'msg': 'Success', 'data': data})
    for detail in details:
        front_developer = ", ".join(eval(detail.front_developer))
        publish_project = ", ".join(eval(detail.publish_project))
        project_total = ", ".join(list(set(projectList)))
        data.append(
            {'requireName': detail.require_name, 'frontDeveloper': front_developer, 'publishProject': publish_project,
             'branch': detail.publish_branch, 'appRenew': detail.app_renew, 'remarks': detail.other_require,
             'projectTotal': project_total})
    return jsonify({'code': 10000, 'msg': 'success', 'data': data})


@publishmanage.route('/publishmanage/afterEnd/uploadImage', methods=['POST'])
# @auth_token.login_required
def afterEndUpLoadImage():
    """
    后端预览生成的邮件图片接口
    """
    file_dir = os.path.join(ProdConfig.UPLOAD_FOLDER2)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    image = request.form.get('image')
    taskName = request.form.get("taskName")
    if len(image) != 0:
        data = image.split(';base64,')[1]
        image_data = base64.b64decode(data)
        image_name = taskName + '.jpg'
        image_url = os.path.join(file_dir, image_name)
        with open(image_url, 'wb') as f:
            f.write(image_data)
        images = PublishManage.query.filter(PublishManage.task_name == taskName, PublishManage.delete_id == 0).update(
            {"image_url": file_dir, "image_realname": image_name})
        try:
            db.session.commit()
            return jsonify({
                'code': 10000,
                'msg': "提交数据成功!"
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                'code': 99999,
                "msg": "提交数据失败!"
            })

    else:
        return jsonify({
            'code': 99995,
            'msg': "图片上传失败!"
        })


@publishmanage.route('/publishmanage/frontEnd/uploadImage', methods=['POST'])
# @auth_token.login_required
def frontEndUpLoadImage():
    """
    前端预览生成的邮件图片接口
    """
    file_dir = os.path.join(ProdConfig.UPLOAD_FOLDER4)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    image = request.form.get('image')
    taskName = request.form.get("taskName")
    if len(image) != 0:
        data = image.split(';base64,')[1]
        image_data = base64.b64decode(data)
        image_name = taskName + '.jpg'
        image_url = os.path.join(file_dir, image_name)
        with open(image_url, 'wb') as f:
            f.write(image_data)
        images = PublishManage.query.filter(PublishManage.task_name == taskName, PublishManage.delete_id == 0).update(
            {"image_url": file_dir, "image_realname": image_name})
        try:
            db.session.commit()
            return jsonify({
                'code': 10000,
                'msg': "提交数据成功!"
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                'code': 99999,
                "msg": "提交数据失败!"
            })

    else:
        return jsonify({
            'code': 99995,
            'msg': "图片上传失败!"
        })


@publishmanage.route('/publishmanage/afterEnd/sendMail', methods=['POST'])
# @auth_token.login_required
def afterEndSendMail():
    """
    后端发布任务发送邮件接口
    """
    img_stream = ''
    taskName = request.form.get("taskName")
    db_imageurl = PublishManage.query.with_entities(PublishManage.image_url).filter_by(task_name=taskName,
                                                                                       delete_id=0).all()
    db_imagerealname = PublishManage.query.with_entities(PublishManage.image_realname).filter_by(task_name=taskName,
                                                                                                 delete_id=0).all()
    root_path = str(db_imageurl[0][0])
    src_name = str(db_imagerealname[0][0])
    image = os.path.join(root_path, src_name)
    with open(image, 'rb') as img_f:
        img_stream = base64.b64encode(img_f.read()).decode('utf-8')
    # 本地开发环境发送邮件接收信息
    # mailContent=Message(subject='【系统发布】'+taskName,sender='tester@ideacome.com',recipients=['shengze.xu@ideacome.com'])
    # 线上环境发送邮件接收信息
    mailContent = Message(subject='【系统发布】' + taskName, sender='tester@ideacome.com',
                          recipients=['ops@ideacome.com', 'prd@ideacome.com', 'pdd@ideacome.com', 'fetd@ideacome.com',
                                      'TD@ideacome.com', 'niipd@ideacome.com'])
    mailContent.html = render_template('email_demo.html', img=img_stream)
    try:
        mail.send(mailContent)
        taskStatus = PublishManage.query.filter(PublishManage.task_name == taskName,
                                                PublishManage.delete_id == 0).update({"task_status": '已发送'})
        db.session.commit()
        return jsonify({
            'code': 10000,
            'msg': "邮件发送成功!"
        })
    except Exception as e:
        return jsonify({
            'code': 99999,
            'msg': "邮件发送失败!"
        })


@publishmanage.route('/publishmanage/frontEnd/sendMail', methods=['POST'])
# @auth_token.login_required
def frontEndSendMail():
    """
    前端发布任务发送邮件接口
    """
    img_stream = ''
    taskName = request.form.get("taskName")
    db_imageurl = PublishManage.query.with_entities(PublishManage.image_url).filter_by(task_name=taskName,
                                                                                       delete_id=0).all()
    db_imagerealname = PublishManage.query.with_entities(PublishManage.image_realname).filter_by(task_name=taskName,
                                                                                                 delete_id=0).all()
    root_path = str(db_imageurl[0][0])
    src_name = str(db_imagerealname[0][0])
    image = os.path.join(root_path, src_name)
    with open(image, 'rb') as img_f:
        img_stream = base64.b64encode(img_f.read()).decode('utf-8')
    # 本地开发环境发送邮件接收信息
    # mailContent=Message(subject='【系统发布】'+taskName,sender='tester@ideacome.com',recipients=['shengze.xu@ideacome.com'])
    # 线上环境发送邮件接收信息
    mailContent = Message(subject='【系统发布】' + taskName, sender='tester@ideacome.com',
                          recipients=['ops@ideacome.com', 'prd@ideacome.com', 'pdd@ideacome.com', 'fetd@ideacome.com',
                                      'TD@ideacome.com', 'niipd@ideacome.com'])
    mailContent.html = render_template('email_demo.html', img=img_stream)
    try:
        mail.send(mailContent)
        taskStatus = PublishManage.query.filter(PublishManage.task_name == taskName,
                                                PublishManage.delete_id == 0).update({"task_status": '已发送'})
        db.session.commit()
        return jsonify({
            'code': 10000,
            'msg': "邮件发送成功!"
        })
    except Exception as e:
        return jsonify({
            'code': 99999,
            'msg': "邮件发送失败!"
        })


@publishmanage.route('/publishmanage/downLoadTemplate', methods=['GET'])
# @auth_token.login_required
def downLoadTemplate():
    """
    #下载测试报告模版接口
    """
    # 本地环境
    # root_path=r'../../../upload/publishmanage/template'
    # 线上环境
    root_path = r'/home/pyproject/upload/publishmanage/template'
    src_name = '测试报告模版.xlsx'
    download_path = os.path.join(root_path, src_name)
    if os.path.isfile(download_path):
        response = send_from_directory(root_path, src_name, as_attachment=True)
        response.headers["Content-Type"] = "application/octet-stream"
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response
    else:
        return jsonify({
            'code': 99999,
            'msg': "下载失败!"
        })


@publishmanage.route('/publishmanage/afterEnd/removeReq', methods=['POST'])
# @auth_token.login_required
def afterEndRemoveReq():
    """
    后端任务编辑页面移除需求接口
    """
    requestParams = request.form
    taskName = requestParams.get('taskName')
    requireName = requestParams.get('requireName')
    requireId = requestParams.get('requireId')
    if requireName != '':
        details = PublishManage_AfterEndDetails.query.filter(PublishManage.delete_id == 0,
                                                             PublishManage.task_name == taskName,
                                                             PublishManage.id == PublishManage_AfterEndDetails.task_id,
                                                             PublishManage_AfterEndDetails.id == requireId).delete(
            synchronize_session=False)
        try:
            db.session.commit()
            return jsonify({
                'code': 10000,
                'msg': "删除数据成功!"
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'code': 99999,
                "msg": "删除数据失败!"
            })
    else:
        return jsonify({
            'code': 99999,
            'msg': "需求名称不能为空!"
        })


@publishmanage.route('/publishmanage/frontEnd/removeReq', methods=['POST'])
# @auth_token.login_required
def frontEndRemoveReq():
    """
    前端任务编辑页面移除需求接口
    """
    requestParams = request.form
    taskName = requestParams.get('taskName')
    requireName = requestParams.get('requireName')
    requireId = requestParams.get('requireId')
    if requireName != '':
        details = PublishManage_FrontEndDetails.query.filter(PublishManage.delete_id == 0,
                                                             PublishManage.task_name == taskName,
                                                             PublishManage.id == PublishManage_FrontEndDetails.task_id,
                                                             PublishManage_FrontEndDetails.id == requireId).delete(
            synchronize_session=False)
        try:
            db.session.commit()
            return jsonify({
                'code': 10000,
                'msg': "删除数据成功!"
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'code': 99999,
                "msg": "删除数据失败!"
            })
    else:
        return jsonify({
            'code': 99999,
            'msg': "需求名称不能为空!"
        })
