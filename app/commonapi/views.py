"""
@File:views.py
@author:zhanfei
@date: 2021/12/3
"""

import os
import json
from flask import request,Flask,jsonify,send_from_directory,make_response,Response,send_file
from werkzeug.utils import secure_filename
from . import commonapi


from app.utils import notEmpty
from app.models import BaseDataSource
from app import db
from app.users.auth import auth_token
from sqlalchemy import or_,and_
from sqlalchemy.sql import func
import requests
import time

commonapi_app=Flask(__name__)


@commonapi.route('/api/developerList', methods=['get'])
#@auth_token.login_required
def developerList():
    """
    开发人员列表(前端+后端)接口
    """
    data=[]
    filters={and_(or_(BaseDataSource.fieldname=='后端开发人员',BaseDataSource.fieldname=='前端开发人员'),BaseDataSource.delete_id==0)}
    filedatas=BaseDataSource.query.filter(*filters).all()
    for filedata in filedatas:
        data.append({'fieldValue':filedata.fieldvalue})
    return jsonify({'code':10000,'msg':'success','data':data})


@commonapi.route('/api/projectNameList', methods=['get'])
#@auth_token.login_required
def projectNameList():
    """
    后端工程列表接口
    """
    data=[]
    filters={and_(BaseDataSource.fieldname=='后端工程',BaseDataSource.delete_id==0)}
    filedatas=BaseDataSource.query.filter(*filters).all()
    for filedata in filedatas:
        data.append({'fieldValue':filedata.fieldvalue})
    return jsonify({'code':10000,'msg':'success','data':data})



@commonapi.route('/api/jarPackageList', methods=['get'])
#@auth_token.login_required
def jarPackageList():
    """
    二方包列表接口
    """
    data=[]
    filters={and_(BaseDataSource.fieldname=='后端二方包',BaseDataSource.delete_id==0)}
    filedatas=BaseDataSource.query.filter(*filters).all()
    for filedata in filedatas:
        data.append({'fieldValue':filedata.fieldvalue})
    return jsonify({'code':10000,'msg':'success','data':data})


@commonapi.route('/api/frontProjectNameList', methods=['get'])
#@auth_token.login_required
def frontProjectNameList():
    """
    前端工程列表接口
    """
    data=[]
    filters={and_(BaseDataSource.fieldname=='前端工程',BaseDataSource.delete_id==0)}
    filedatas=BaseDataSource.query.filter(*filters).all()
    for filedata in filedatas:
        data.append({'fieldValue':filedata.fieldvalue})
    return jsonify({'code':10000,'msg':'success','data':data})


@commonapi.route('/api/testerList', methods=['get'])
#@auth_token.login_required
def testerList():
    """
    测试人员列表接口
    """
    data=[]
    filters={and_(BaseDataSource.fieldname=='测试人员',BaseDataSource.delete_id==0)}
    filedatas=BaseDataSource.query.filter(*filters).all()
    for filedata in filedatas:
        data.append({'fieldValue':filedata.fieldvalue})
    return jsonify({'code':10000,'msg':'success','data':data})



@commonapi.route('/api/afterdeveloperList', methods=['get'])
#@auth_token.login_required
def afterdeveloperList():
    """
    开发人员列表(后端)接口
    """
    data=[]
    filters={and_(BaseDataSource.fieldname=='后端开发人员',BaseDataSource.delete_id==0)}
    filedatas=BaseDataSource.query.filter(*filters).all()
    for filedata in filedatas:
        data.append({'fieldValue':filedata.fieldvalue})
    return jsonify({'code':10000,'msg':'success','data':data})



@commonapi.route('/api/frontdeveloperList', methods=['get'])
#@auth_token.login_required
def frontdeveloperList():
    """
    开发人员列表(前端)接口
    """
    data=[]
    filters={and_(BaseDataSource.fieldname=='前端开发人员',BaseDataSource.delete_id==0)}
    filedatas=BaseDataSource.query.filter(*filters).all()
    for filedata in filedatas:
        data.append({'fieldValue':filedata.fieldvalue})
    return jsonify({'code':10000,'msg':'success','data':data})