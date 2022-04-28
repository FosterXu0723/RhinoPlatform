"""
@File:views.py
@author:zhanfei
@date: 2021/02/22
"""

import os
import json
from flask import request,Flask,jsonify,send_from_directory,make_response,Response,send_file
from werkzeug.utils import secure_filename
from . import errormsgmanage


from app.utils import notEmpty
from app.models import PullError_Task
from app.models import PullError_details
from app.models import ProjectBelongBus
from app.models import StaffBasicInfo
from app import db
from app.users.auth import auth_token
from sqlalchemy import or_,and_,distinct
from sqlalchemy.sql import func
import requests
import time
import emoji,re
import xlsxwriter
from io import BytesIO

errormsgmanage_app=Flask(__name__)



@errormsgmanage.route('/errormsgmanage/pullError', methods=['POST'])
#@auth_token.login_required
def pullError():
    """
    拉取报错信息接口
    """
    requestParams = request.form
    pullStartDate=requestParams.get('pullStartDate')
    pullEndDate=requestParams.get('pullEndDate')

    #三通提供的线上服务器错误信息收集接口
    url='http://114.55.2.72:6001/getData'
    #pullDateMin=db.session.query(func.min(PullError_Task.task_enddate)).scalar()
    pullDateMax=db.session.query(func.max(PullError_Task.task_enddate)).scalar()
    if pullStartDate != "" and pullEndDate !="":
        if str(pullStartDate)<str(pullDateMax):
            return jsonify({'code':99991,'msg':'拉取时间范围可能存在重复！'})
        elif pullDateMax=='None' or str(pullStartDate)>=str(pullDateMax):
            #调用线上服务器错误信息收集接口
            reqdata={'beginDate':pullStartDate,'endDate':pullEndDate}
            errorinfos=requests.get(url,reqdata).json()
        if errorinfos['status']==0:
        #往任务表和详情表插入数据
            task= PullError_Task(task_startdate=pullStartDate,task_enddate=pullEndDate,task_status='未开始')
            db.session.add(task)
            db.session.flush()
            #添加到缓存后,取任务ID,后面存入详情表时要用
            taskid=task.id
            errorinfo=errorinfos['data']
            if errorinfo=={}:
                return jsonify({'code':99995,'msg':"无错误信息!"})
            else:
                try:
                    for errors in errorinfo.values():
                        projectname=errors['project_name']
                        if errors['time_stamp']=="":
                            otherStyleTime=''
                        else:
                            timeStamp=int(errors['time_stamp'][0:10])
                            timeArray=time.localtime(timeStamp)
                            otherStyleTime=time.strftime("%Y-%m-%d %H:%M:%S",timeArray)
                        filters={ProjectBelongBus.project==projectname,ProjectBelongBus.delete_id==0}
                        filedatas=ProjectBelongBus.query.filter(*filters).limit(1).all()
                        if len(filedatas)==0:
                            emoji_str=emoji.demojize(errors['message_data'][0:3000])
                            error_str=re.sub(r':(.*?):','',emoji_str).strip()
                            details= PullError_details(task_id=taskid,project_name=projectname,belong_bus='公共',error_class=errors['errorClass'],error_info=error_str,
                                error_times=errors['number'],error_date=str(otherStyleTime),developer='岳老三',tester='杨无邪',error_status='未认领')
                            db.session.add(details)
                            #return jsonify({'code': 99998, 'msg': '未找到工程对应的归属业务'})
                               
                        else:
                            filedata=filedatas[0]
                            emoji_str=emoji.demojize(errors['message_data'][0:3000])
                            error_str=re.sub(r':(.*?):','',emoji_str).strip()
                            details= PullError_details(task_id=taskid,project_name=filedata.project,belong_bus=filedata.business,error_class=errors['errorClass'],error_info=error_str,
                                error_times=errors['number'],error_date=str(otherStyleTime),developer=filedata.developer,tester=filedata.tester,error_status='未认领')
                            db.session.add(details)
                    db.session.commit()
                    return jsonify({'code':10000,'msg':"提交数据成功!"})
            
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'code':99999,"msg":"提交数据失败!"})
                        
        else:
            return jsonify({'code':99992,'msg':'拉取失败,请稍后再试！'})
    else:
        return jsonify({'code':99993,'msg':'拉取时间选择有问题,请检查！'})


@errormsgmanage.route('/errormsgmanage/pullRecList', methods=['POST'])
#@auth_token.login_required
def pullRecList():
    """
    拉取记录列表接口
    """
    data=[]
    requestParams = request.form
    taskID=requestParams.get('taskID')
    createStartDate=requestParams.get('createStartDate')
    createEndDate=requestParams.get('createEndDate')
    cycleStatus=requestParams.get('cycleStatus')
    page=int((requestParams.get('page')))
    pageSize=int(requestParams.get('pageSize'))

    #在任务列表查询时,根据详情表中的错误状态更新任务表中的状态
    taskids=db.session.query(PullError_Task.id).distinct(PullError_Task.id)
    for taskid in taskids:
        statusList=[]
        errorstatuss=db.session.query(PullError_details.error_status).filter(PullError_details.task_id==str(taskid[0])).distinct(PullError_details.error_status)
        for errorstatus in errorstatuss:
            statusList.append(str(errorstatus[0]))
        if list(set(statusList))==['未认领']:
            tasks=PullError_Task.query.filter(PullError_Task.id==str(taskid[0]),PullError_Task.delete_id==0).update({"task_status":'未开始'},synchronize_session=False)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
        elif ('已指派' in statusList) or ('解决中' in statusList) or ('已解决待发布' in statusList) or ('延期解决' in statusList) or ('险企问题未解决' in statusList):
            tasks=PullError_Task.query.filter(PullError_Task.id==str(taskid[0]),PullError_Task.delete_id==0).update({"task_status":'进行中'},synchronize_session=False)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
        elif ('未认领' not in statusList) and ('已指派' not in statusList) and ('解决中' not in statusList) and ('已解决待发布' not in statusList) and ('延期解决' not in statusList) and ('险企问题未解决' not in statusList):
            tasks=PullError_Task.query.filter(PullError_Task.id==str(taskid[0]),PullError_Task.delete_id==0).update({"task_status":'全部解决'},synchronize_session=False)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()


    #根据前端传入的查询条件进行查询
    if createStartDate !='' and createEndDate !='' and cycleStatus !='' and taskID !='':
        filters={and_(and_(PullError_Task.create_time>=createStartDate,PullError_Task.create_time<=createEndDate,PullError_Task.id==taskID,PullError_Task.task_status==cycleStatus),PullError_Task.delete_id==0)}
        filedatas=PullError_Task.query.filter(*filters).order_by(db.desc(PullError_Task.create_time)).offset((page-1) * pageSize).limit(pageSize).all()
        totaldatas=PullError_Task.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code':10000,'msg':'Success','data':data,'total':0})
        else:
            for filedata in filedatas:
                data.append({'cycleId':filedata.id,'pullDateRange':str(filedata.task_startdate)+'--'+str(filedata.task_enddate),'cycleCreateDate':str(filedata.create_time),'cycleStatusTable':filedata.task_status})
            return jsonify({'code':10000,'msg':'success','data':data,'total':totaldatas})

    elif createStartDate=='' and createEndDate=='' and cycleStatus !='' and taskID !='':
        filters={and_(and_(PullError_Task.task_status==cycleStatus,PullError_Task.id==taskID),PullError_Task.delete_id==0)}
        filedatas=PullError_Task.query.filter(*filters).order_by(db.desc(PullError_Task.create_time)).offset((page-1) * pageSize).limit(pageSize).all()
        totaldatas=PullError_Task.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code':10000,'msg':'Success','data':data,'total':0})
        else:
            for filedata in filedatas:
                data.append({'cycleId':filedata.id,'pullDateRange':str(filedata.task_startdate)+'--'+str(filedata.task_enddate),'cycleCreateDate':str(filedata.create_time),'cycleStatusTable':filedata.task_status})
            return jsonify({'code':10000,'msg':'success','data':data,'total':totaldatas})

    elif createStartDate !='' and createEndDate !='' and cycleStatus=='' and taskID !='':
        filters={and_(and_(PullError_Task.create_time>=createStartDate,PullError_Task.create_time<=createEndDate,PullError_Task.id==taskID),PullError_Task.delete_id==0)}
        filedatas=PullError_Task.query.filter(*filters).order_by(db.desc(PullError_Task.create_time)).offset((page-1) * pageSize).limit(pageSize).all()
        totaldatas=PullError_Task.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code':10000,'msg':'Success','data':data,'total':0})
        else:
            for filedata in filedatas:
                data.append({'cycleId':filedata.id,'pullDateRange':str(filedata.task_startdate)+'--'+str(filedata.task_enddate),'cycleCreateDate':str(filedata.create_time),'cycleStatusTable':filedata.task_status})
            return jsonify({'code':10000,'msg':'success','data':data,'total':totaldatas})

    elif createStartDate !='' and createEndDate !='' and cycleStatus !='' and taskID=='':
        filters={and_(and_(PullError_Task.create_time>=createStartDate,PullError_Task.create_time<=createEndDate,PullError_Task.task_status==cycleStatus),PullError_Task.delete_id==0)}
        filedatas=PullError_Task.query.filter(*filters).order_by(db.desc(PullError_Task.create_time)).offset((page-1) * pageSize).limit(pageSize).all()
        totaldatas=PullError_Task.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code':10000,'msg':'Success','data':data,'total':0})
        else:
            for filedata in filedatas:
                data.append({'cycleId':filedata.id,'pullDateRange':str(filedata.task_startdate)+'--'+str(filedata.task_enddate),'cycleCreateDate':str(filedata.create_time),'cycleStatusTable':filedata.task_status})
            return jsonify({'code':10000,'msg':'success','data':data,'total':totaldatas})
    
    elif createStartDate=='' and createEndDate=='' and cycleStatus=='' and taskID !='':
        filters={and_(PullError_Task.id==taskID,PullError_Task.delete_id==0)}
        filedatas=PullError_Task.query.filter(*filters).order_by(db.desc(PullError_Task.create_time)).offset((page-1) * pageSize).limit(pageSize).all()
        totaldatas=PullError_Task.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code':10000,'msg':'Success','data':data,'total':0})
        else:
            for filedata in filedatas:
                data.append({'cycleId':filedata.id,'pullDateRange':str(filedata.task_startdate)+'--'+str(filedata.task_enddate),'cycleCreateDate':str(filedata.create_time),'cycleStatusTable':filedata.task_status})
            return jsonify({'code':10000,'msg':'success','data':data,'total':totaldatas})

    elif createStartDate=='' and createEndDate=='' and cycleStatus !='' and taskID=='':
        filters={and_(PullError_Task.task_status==cycleStatus,PullError_Task.delete_id==0)}
        filedatas=PullError_Task.query.filter(*filters).order_by(db.desc(PullError_Task.create_time)).offset((page-1) * pageSize).limit(pageSize).all()
        totaldatas=PullError_Task.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code':10000,'msg':'Success','data':data,'total':0})
        else:
            for filedata in filedatas:
                data.append({'cycleId':filedata.id,'pullDateRange':str(filedata.task_startdate)+'--'+str(filedata.task_enddate),'cycleCreateDate':str(filedata.create_time),'cycleStatusTable':filedata.task_status})
            return jsonify({'code':10000,'msg':'success','data':data,'total':totaldatas})

    elif createStartDate !='' and createEndDate !='' and cycleStatus=='' and taskID=='':
        filters={and_(and_(PullError_Task.create_time>=createStartDate,PullError_Task.create_time<=createEndDate),PullError_Task.delete_id==0)}
        filedatas=PullError_Task.query.filter(*filters).order_by(db.desc(PullError_Task.create_time)).offset((page-1) * pageSize).limit(pageSize).all()
        totaldatas=PullError_Task.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code':10000,'msg':'Success','data':data,'total':0})
        else:
            for filedata in filedatas:
                data.append({'cycleId':filedata.id,'pullDateRange':str(filedata.task_startdate)+'--'+str(filedata.task_enddate),'cycleCreateDate':str(filedata.create_time),'cycleStatusTable':filedata.task_status})
            return jsonify({'code':10000,'msg':'success','data':data,'total':totaldatas})


    else:
        filters={PullError_Task.delete_id==0}
        filedatas=PullError_Task.query.filter(*filters).order_by(db.desc(PullError_Task.create_time)).offset((page-1) * pageSize).limit(pageSize).all()
        totaldatas=PullError_Task.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code':10000,'msg':'Success','data':data,'total':0})
        else:
            for filedata in filedatas:
                data.append({'cycleId':filedata.id,'pullDateRange':str(filedata.task_startdate)+'--'+str(filedata.task_enddate),'cycleCreateDate':str(filedata.create_time),'cycleStatusTable':filedata.task_status})
            return jsonify({'code':10000,'msg':'success','data':data,'total':totaldatas})





@errormsgmanage.route('/errormsgmanage/errorInfoDetail', methods=['POST'])
#@auth_token.login_required
def errorInfoDetail():
    """
    错误信息查看详情接口
    """
    data={}
    requestParams = request.form
    taskID=requestParams.get('taskID')
    errorID=requestParams.get('errorID')
    try:
        filters={PullError_details.id==errorID,PullError_details.task_id==taskID,PullError_details.delete_id==0}
        filedatas=PullError_details.query.filter(*filters).limit(1).all()
        filedata=filedatas[0]
        data={'projectName':filedata.project_name,'belongBus':filedata.belong_bus,'errorClass':filedata.error_class,'errorInfo':filedata.error_info,'errorTimes':filedata.error_times,'errorDate':filedata.error_date,'Developer':filedata.developer,'Tester':filedata.tester,'errorReason':filedata.error_reason,'errorStatus':filedata.error_status,'pubDate':filedata.pub_date,'errorRemarks':filedata.error_remarks}
        return jsonify({'code':10000,'msg':'success','data':data})
    except Exception as e:
        return jsonify({'code':99999,'msg':'error'})



@errormsgmanage.route('/errormsgmanage/errorInfoList', methods=['POST'])
#@auth_token.login_required
def errorInfoList():
    """
    错误信息列表接口
    """
    data=[]
    requestParams = request.form
    taskID=requestParams.get('taskID')
    errorID=requestParams.get('errorID')
    projectName=requestParams.get('projectName')
    belongBus=requestParams.get('belongBus')
    dealStatus=requestParams.get('dealStatus')
    developer=requestParams.get('developer')
    tester=requestParams.get('tester')
    page=int((requestParams.get('page')))
    pageSize=int(requestParams.get('pageSize'))
    try:
        filters={PullError_details.id.like("%"+errorID+"%") if errorID is not None else "",PullError_details.project_name.like("%"+projectName+"%") if projectName is not None else "",PullError_details.belong_bus.like("%"+belongBus+"%") if belongBus is not None else "",PullError_details.error_status.like("%"+dealStatus+"%") if dealStatus is not None else "",PullError_details.developer.like("%"+developer+"%") if developer is not None else "",PullError_details.tester.like("%"+tester+"%") if tester is not None else "",PullError_details.task_id==taskID}
        filedatas=PullError_details.query.filter_by(delete_id=0).filter(*filters).order_by(db.desc(PullError_details.create_time)).offset((page-1) * pageSize).limit(pageSize).all()
        totaldatas=PullError_details.query.filter(*filters).count()
        if len(filedatas) == 0:
            return jsonify({'code':10000,'msg':'Success','data':data,'total':0})
        else:
            for filedata in filedatas:
                data.append({'errorID':filedata.id,'errorProject':filedata.project_name,'errorBus':filedata.belong_bus,'errorSolver':filedata.developer,'errorTester':filedata.tester,'errorStatus':filedata.error_status,'errorTimes':filedata.error_times,'errorDate':filedata.error_date,'errorInfo':filedata.error_info,'errorReason':filedata.error_reason})
            return jsonify({'code':10000,'msg':'success','data':data,'total':totaldatas})
    except Exception as e:
        return jsonify({'code':99999,'msg':'error'})


@errormsgmanage.route('/errormsgmanage/errorInfoEdit', methods=['POST'])
#@auth_token.login_required
def errorInfoEdit():
    """
    错误信息编辑详情接口
    """
    data={}
    requestParams = request.form
    taskID=requestParams.get('taskID')
    errorID=requestParams.get('errorID')
    try:
        filters={PullError_details.id==errorID,PullError_details.task_id==taskID,PullError_details.delete_id==0}
        filedatas=PullError_details.query.filter(*filters).limit(1).all()
        filedata=filedatas[0]
        data={'errorID':filedata.id,'projectName':filedata.project_name,'errorInfo':filedata.error_info,'belongBus':filedata.belong_bus,'Developer':filedata.developer,'Tester':filedata.tester,'errorStatus':filedata.error_status,'errorReason':filedata.error_reason,'pubDate':filedata.pub_date,'errorRemarks':filedata.error_remarks}
        return jsonify({'code':10000,'msg':'success','data':data})
    except Exception as e:
        return jsonify({'code':99999,'msg':'error'})



@errormsgmanage.route('/errormsgmanage/errorInfoSave', methods=['POST'])
#@auth_token.login_required
def errorInfoSave():
    """
    保存错误信息接口
    """
    data={}
    requestParams = request.form
    taskID=requestParams.get('taskID')
    errorID=requestParams.get('errorID')
    belongBus=requestParams.get('belongBus')
    Developer=requestParams.get('Developer')
    Tester=requestParams.get('Tester')
    errorStatus=requestParams.get('errorStatus')
    errorReason=requestParams.get('errorReason')
    pubDate=requestParams.get('pubDate')
    errorRemarks=requestParams.get('errorRemarks')
    if errorStatus=='未认领' or errorStatus=='':
        return jsonify({'code':99998,'msg':'处理状态不能为未认领或者为空!'})
    else:
        details=PullError_details.query.filter(PullError_details.task_id==taskID,PullError_details.id==errorID,PullError_details.delete_id==0).update(
            {"belong_bus":belongBus,"developer":Developer,"tester":Tester,"error_status":errorStatus,"error_reason":errorReason,"pub_date":pubDate,"error_remarks":errorRemarks},synchronize_session=False)
        try:
            db.session.commit()
            return jsonify({'code':10000,'msg':'数据处理完成!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'code':99999,'msg':'数据处理失败!'})





@errormsgmanage.route('/errormsgmanage/errorInfoDown', methods=['POST'])
#@auth_token.login_required
def errorInfoDown():
    """
    错误信息下载接口
    """
    data=[]
    requestParams = request.form
    taskID=requestParams.get('taskID')
    errorID=requestParams.get('errorID')
    projectName=requestParams.get('projectName')
    belongBus=requestParams.get('belongBus')
    dealStatus=requestParams.get('dealStatus')
    developer=requestParams.get('developer')
    tester=requestParams.get('tester')
    try:
        taskStartDate=PullError_Task.query.with_entities(PullError_Task.task_startdate).filter(PullError_Task.id==taskID,PullError_Task.delete_id==0).all()
        taskEndDate=PullError_Task.query.with_entities(PullError_Task.task_enddate).filter(PullError_Task.id==taskID,PullError_Task.delete_id==0).all()
        filters={PullError_details.id.like("%"+errorID+"%") if errorID is not None else "",PullError_details.project_name.like("%"+projectName+"%") if projectName is not None else "",PullError_details.belong_bus.like("%"+belongBus+"%") if belongBus is not None else "",PullError_details.error_status.like("%"+dealStatus+"%") if dealStatus is not None else "",PullError_details.developer.like("%"+developer+"%") if developer is not None else "",PullError_details.tester.like("%"+tester+"%") if tester is not None else "",PullError_details.task_id==taskID}
        filedatas=PullError_details.query.filter_by(delete_id=0).filter(*filters).order_by(db.desc(PullError_details.create_time)).all()
        if len(filedatas) == 0:
            #创建IO对象
            output=BytesIO()
            #先创建一个book，直接写到io中
            workbook=xlsxwriter.Workbook(output,{'in_memory':True})
            #写数据到excel
            sheet=workbook.add_worksheet('sheet1')
            fileds=['工程名','业务线','报错涉及的class','报错日志详细信息','数量','开发负责人','测试负责人','处理状态','出现时间范围','失败原因','备注']
            sheet.write_row('A1',fileds)
            workbook.close()
            #找到流的起始位置
            output.seek(0)
            resp=make_response(output.getvalue())
            output.close()
            resp.headers['Content-Type'] = "application/octet-stream"
            #resp.headers["Cache-Control"] = "no-cache"
            resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
            resp.headers["Content-Disposition"] = "attachment;filename=download.xlsx"
            return resp
            
        else:
            #创建IO对象
            output=BytesIO()
            #先创建一个book，直接写到io中
            workbook=xlsxwriter.Workbook(output,{'in_memory':True})
            #写数据到excel
            sheet=workbook.add_worksheet('sheet1')
            fileds=['工程名','业务线','报错涉及的class','报错日志详细信息','数量','开发负责人','测试负责人','处理状态','出现时间范围','失败原因','备注']
            sheet.write_row('A1',fileds)
            for i,filedata in zip(range(len(filedatas)),filedatas):
                dataList=[filedata.project_name,filedata.belong_bus,filedata.error_class,filedata.error_info,filedata.error_times,filedata.developer,filedata.tester,filedata.error_status,filedata.error_date,filedata.error_reason,filedata.error_remarks]
                row=[]
                for d in dataList:
                    row.append(d)
                sheet.write_row('A'+str(i+2),row)
            workbook.close()
            #找到流的起始位置
            output.seek(0)
            resp=make_response(output.getvalue())
            output.close()
            resp.headers['Content-Type'] = "application/octet-stream"
            #resp.headers["Cache-Control"] = "no-cache"
            resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
            resp.headers["Content-Disposition"] = "attachment;filename=download.xlsx"
            return resp
    except Exception as e:
        return jsonify({'code':99999,'msg':'导出异常'})




@errormsgmanage.route('/errormsgmanage/dingTalk', methods=['POST'])
#@auth_token.login_required
def dingTalk():
    """
    钉一下接口
    """
    data={}
    requestParams = request.form
    taskID=requestParams.get('taskID')
    errorID=requestParams.get('errorID')
    try:
        filters={PullError_details.id==errorID,PullError_details.task_id==taskID,PullError_details.delete_id==0}
        filedatas=PullError_details.query.filter(*filters).limit(1).all()
        filedata=filedatas[0]
        taskStartDate=PullError_Task.query.with_entities(PullError_Task.task_startdate).filter(PullError_Task.id==taskID,PullError_Task.delete_id==0).all()
        taskEndDate=PullError_Task.query.with_entities(PullError_Task.task_enddate).filter(PullError_Task.id==taskID,PullError_Task.delete_id==0).all()
        staffPhone=StaffBasicInfo.query.with_entities(StaffBasicInfo.phone).filter(StaffBasicInfo.name==str(filedata.developer),StaffBasicInfo.delete_id==0).all()
        url="https://oapi.dingtalk.com/robot/send?access_token=1d41e4dd2e72d51a79da979ee4d729626f69e90cad4f1d1e97c75cf0e22ab743"
        headers={"Content-Type":"application/json;charset=utf-8"}
        data={
            "msgtype": "markdown",
            "markdown": {
                "title":"线上错误信息跟踪提醒",
                "text":"【问题待处理提醒】周期编号:"+str(taskID)+"  "+"时间范围在"+str(taskStartDate[0][0])+"~"+str(taskEndDate[0][0])+"  "+"@"+str(staffPhone[0][0])+"\n"
                        ">1.errorID:"+"  "+str(filedata.id)+"\n\n"
                        ">2.出现具体时间:"+"  "+str(filedata.error_date)+"\n\n"
                        ">3.处理状态:"+"  "+str(filedata.error_status)+"\n\n"
                        ">4.应用名称:"+"  "+str(filedata.project_name)+"\n\n"
                        ">5.所属业务:"+"  "+str(filedata.belong_bus)+"\n\n"
                        ">6.开发负责人:"+"  "+str(filedata.developer)+"\n\n"
                        ">7.测试负责人:"+"  "+str(filedata.tester)+"\n\n"
            },
            "at": {
                "atMobiles": [str(staffPhone[0][0])],
                "isAtAll": False
            }
        }
        result=requests.post(url=url,headers=headers,data=json.dumps(data))
        return jsonify({'code':10000,'msg':'success'})
    except Exception as e:
        return jsonify({'code':99999,'msg':'error'})
