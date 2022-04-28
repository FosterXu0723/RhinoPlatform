"""
@File:views.py
@author:zhanfei
@date: 2021/01/25
"""

from flask import jsonify, request

from app.utils import notEmpty
from . import tctransform
from app.models import TcTransForm
from app.models import TransForm_Modules
from app import db
from app.users.auth import auth_token
from sqlalchemy import or_


@tctransform.route('/tctransform/createcsv', methods=['POST'])
#@auth_token.login_required
def createCsv():
    """
    提交生成CSV文件数据接口
    """
    requestParams = request.form
    caseFileName = requestParams.get("caseFileName")
    caseBelongModule = requestParams.get("caseBelongModule")
    operator = requestParams.get("operator")
    fileUrl = requestParams.get("fileUrl")
    casefile= TcTransForm(case_file_name=caseFileName,case_belong_module=caseBelongModule,operators=operator,file_url=fileUrl)
    try:
        db.session.add(casefile)
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


@tctransform.route('/tctransform/list', methods=['POST'])
#@auth_token.login_required
def tctransform_list():
    """
    已生成的CSV文件数据列表接口
    """
    data=[]
    caseFileName=request.form.get('caseFileName')
    caseBelongModule=request.form.get('caseBelongModule')
    createTime=request.form.get('createTime')
    page = int(request.form.get('page'))
    pageSize = int(request.form.get('pageSize'))
    filters={TcTransForm.case_file_name.like("%"+caseFileName+"%"),TcTransForm.case_belong_module.like("%"+caseBelongModule+"%"),TcTransForm.create_time.like("%"+createTime+"%")}
    filedatas=TcTransForm.query.filter(*filters).offset((page-1) * pageSize).limit(pageSize).all()
    if len(filedatas) == 0:
        return jsonify({'code':10000,'msg':'Success','data':data})
    else:
        for filedata in filedatas:
            data.append({'fileId':filedata.id,'caseFileName':filedata.case_file_name,'caseBelongModule':filedata.case_belong_module,'operator':filedata.operators,'createTime':str(filedata.create_time)})
        return jsonify({'code':10000,'msg':'success','data':data})




@tctransform.route('/tctransform/sysmodules', methods=['GET'])
#@auth_token.login_required
def sysModules():
    """
    CSV文件归属的系统模块接口
    """
    MainMenus=TransForm_Modules.query.with_entities(TransForm_Modules.MainMenus).filter(TransForm_Modules.MenuStatus==1).distinct().all()
    data=[]
    for MainMenu in MainMenus:
        ChildMenuData=[]
        filters={TransForm_Modules.MainMenus==MainMenu[0]}
        ChildMenus=TransForm_Modules.query.with_entities(TransForm_Modules.ChildMenus).filter(*filters).distinct().all()
        for ChildMenu in ChildMenus:
            ChildMenuData.append(ChildMenu[0])
        data.append({"MainMenu":MainMenu[0],"ChildMenu":ChildMenuData})
    return jsonify({
            'code':10000,
            'msg':'Success',
            'data':data
        })