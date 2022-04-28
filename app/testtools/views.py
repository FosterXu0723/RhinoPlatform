"""
@File:views.py
@author:zhanfei
@date: 2021/02/22
"""

import os
import json
from flask import request,Flask,jsonify,send_from_directory,make_response,Response,send_file
from werkzeug.utils import secure_filename
from . import testtools


from app.utils import notEmpty
from app.models import TestTools
from app import db
from app.users.auth import auth_token
from sqlalchemy import or_,and_

testtools_app=Flask(__name__)

#本地环境地址
#UPLOAD_FOLDER=r'../../../upload/testtool'
#线上环境地址
UPLOAD_FOLDER=r'/home/pyproject/upload/testtool'
testtools_app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))


ALLOWED_EXTENSIONS=set(['exe','py'])





def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS



@testtools.route('/testtools/uploadtools', methods=['POST'])
#@auth_token.login_required
def uploadtools():
    """
    上传测试工具接口
    """
    file_dir=os.path.join(testtools_app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f=request.files['file']
    toolName=request.form.get("toolName")
    toolAuthor=request.form.get("toolAuthor")
    if f and allowed_file(f.filename):
        fname=secure_filename(f.filename)
        f.save(os.path.join(file_dir,fname))
        #tools= TestTools(tool_name=toolName,tool_author=toolAuthor,tool_url=file_dir,tool_realname=fname)
        tool_names=TestTools.query.with_entities(TestTools.tool_name).all()
        for tool_name in tool_names:
            if toolName==tool_name[0]:
                return jsonify({
                    'code':99998,
                    'msg':"测试工具名称已存在!"
                })
        tools= TestTools(tool_name=toolName,tool_author=toolAuthor,tool_url=file_dir,tool_realname=fname)
        try:
            db.session.add(tools)
            db.session.commit()
            return jsonify({
                'code':10000,
                'msg':"提交数据成功!"
                })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                'code':99999,
                "msg":"提交数据失败!"
                })
                
    else:
        return jsonify({
            'code':99999,
            'msg':"提交数据失败!"
            })



@testtools.route('/testtools/toolsList', methods=['POST'])
#@auth_token.login_required
def toolsList():
    """
    已上传的工具列表接口
    """
    data=[]
    requestParams = request.form
    toolName=requestParams.get('toolName')
    toolAuthor=requestParams.get('toolAuthor')
    page=int((requestParams.get('page')))
    pageSize=int(requestParams.get('pageSize'))
    if toolName !='' and toolAuthor !='':
        filters={and_(and_(TestTools.tool_name.like("%"+toolName+"%"),TestTools.tool_author==toolAuthor),TestTools.delete_id==0)}
        filedatas=TestTools.query.filter(*filters).order_by(db.desc(TestTools.create_time)).offset((page-1) * pageSize).limit(pageSize).all()
        totaldatas=TestTools.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code':10000,'msg':'Success','data':data,'total':0})
        else:
            for filedata in filedatas:
                data.append({'toolName':filedata.tool_name,'fileName':filedata.tool_realname,'toolAuthor':filedata.tool_author,'createTime':str(filedata.create_time)})
            return jsonify({'code':10000,'msg':'success','data':data,'total':totaldatas})

    elif toolName=='' and toolAuthor !='':
        filters={and_(and_(TestTools.tool_name.like("%"+toolName+"%"),TestTools.tool_author==toolAuthor),TestTools.delete_id==0)}
        filedatas=TestTools.query.filter(*filters).order_by(db.desc(TestTools.create_time)).offset((page-1) * pageSize).limit(pageSize).all()
        totaldatas=TestTools.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code':10000,'msg':'Success','data':data,'total':0})
        else:
            for filedata in filedatas:
                data.append({'toolName':filedata.tool_name,'fileName':filedata.tool_realname,'toolAuthor':filedata.tool_author,'createTime':str(filedata.create_time)})
            return jsonify({'code':10000,'msg':'success','data':data,'total':totaldatas})

    else:
        filters={and_(or_(TestTools.tool_name.like("%"+toolName+"%"),TestTools.tool_author==toolAuthor),TestTools.delete_id==0)}
        filedatas=TestTools.query.filter(*filters).order_by(db.desc(TestTools.create_time)).offset((page-1) * pageSize).limit(pageSize).all()
        totaldatas=TestTools.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code':10000,'msg':'Success','data':data,'total':0})
        else:
            for filedata in filedatas:
                data.append({'toolName':filedata.tool_name,'fileName':filedata.tool_realname,'toolAuthor':filedata.tool_author,'createTime':str(filedata.create_time)})
            return jsonify({'code':10000,'msg':'success','data':data,'total':totaldatas})






@testtools.route('/testtools/deleteTools', methods=['POST'])
#@auth_token.login_required
def deleteTools():
    """
    删除列表中的工具接口
    """
    requestParams = request.form
    toolName=requestParams.get('toolName')
    if toolName !='':
        tool=TestTools.query.filter_by(tool_name=toolName).update({"delete_id":1})
        try:
            db.session.commit()
            return jsonify({
                'code':10000,
                'msg':"删除数据成功!"
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'code':99999,
                "msg":"删除数据失败!"
            })
    else:
        return jsonify({
            'code':99999,
            'msg':"删除数据失败!"
            })





@testtools.route('/testtools/downLoadTools', methods=['POST'])
#@auth_token.login_required
def downLoadTools():
    """
    #下载工具接口
    """
    requestParams = request.form
    toolName=requestParams.get('toolName')
    fileName=requestParams.get('fileName')
    db_toolurl=TestTools.query.with_entities(TestTools.tool_url).filter_by(tool_realname=fileName,tool_name=toolName,delete_id=0).all()
    db_toolrealname=TestTools.query.with_entities(TestTools.tool_realname).filter_by(tool_realname=fileName,tool_name=toolName,delete_id=0).all()
    root_path=str(db_toolurl[0][0])
    src_name=str(db_toolrealname[0][0])
    upload_path=os.path.join(root_path,src_name)
    if os.path.isfile(upload_path):
        response=send_from_directory(root_path,src_name,as_attachment=True)
        response.headers["Content-Type"]="application/octet-stream"
        response.headers["Access-Control-Expose-Headers"]="Content-Disposition"
        #response.headers["Content-Disposition"]="attachment;filename={};".format(src_name)


        #print('response:',response)
        
        return response

        '''return {
            'code':10000,
            'msg':"下载成功!",
            'filename':src_name,
            'data':response
            }'''
    else:
        return jsonify({
            'code':99999,
            'msg':"下载失败!"
            })


