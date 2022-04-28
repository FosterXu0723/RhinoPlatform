#  date:  2021/4/23
#  Author:  jinmu
#  Description:


from . import testreport
from flask import Flask, request, json,jsonify
from app import db
from app.models import ReportResult
from app.models import CaseResult
from app.models import Testcase

from app.utils.BatchTranlateYml import yml2testcase




@testreport.route('/list',methods=['POST'])
def list():
    '''
    列表页查询接口，返回查询的报告
    :return:
    '''

    reportName = request.form.get('reportName') or ''
    Status = request.form.get('reportStatus') or ''
    if Status == '':
        reportStatus = ''
    elif Status == '选项1':
        reportStatus =(1,2)
    elif Status == '选项2':
        reportStatus = (1,)
    else:
        reportStatus = (2,)
    creatDate = request.form.get('date') or ''
    page = int(request.form.get('page'))
    per_page = int(request.form.get('per_page'))
    if all([reportName,reportStatus,creatDate]):#列举出各种情况 然后分情况去数据库查询结果
        report = ReportResult.query.filter(ReportResult.reportName==reportName,ReportResult.reportStatus.in_(reportStatus),ReportResult.creatDate.like("%" + creatDate + "%")).paginate(page, per_page, error_out=False)
        returnReport = report.items
        total = report.total
        if report.iter_pages():#判断后返回前端页码
            pages=0
        else:
            pages = max(report.iter_pages())
        tableData = []
        for item in returnReport:
            reportData = item.to_dict()
            tableData.append(reportData)
        if tableData:
            return jsonify({'code': '200', 'errmsg': '查询成功！', 'total':total,'pages':pages,"tableData": tableData})
        else:
            return jsonify({'code': '200', 'errmsg': '查询结果为空！'})
    elif reportName != '' and reportStatus != '' and creatDate == '':
        report = ReportResult.query.filter(ReportResult.reportName==reportName,ReportResult.reportStatus.in_(reportStatus)).paginate(page, per_page, error_out=False)
        returnReport = report.items
        total = report.total
        if report.iter_pages():
            pages=0
        else:
            pages = max(report.iter_pages())
        tableData = []
        for item in returnReport:
            reportData = item.to_dict()
            tableData.append(reportData)
        if tableData:
            return jsonify({'code': '200', 'errmsg': '查询成功！', 'total':total,'pages':pages,"tableData": tableData})
        else:
            return jsonify({'code': '200', 'errmsg': '查询结果为空！'})
    elif reportName != '' and reportStatus == '' and creatDate != '':
        report = ReportResult.query.filter(ReportResult.reportName==reportName,ReportResult.creatDate.like("%" + creatDate + "%")).paginate(page, per_page, error_out=False)
        returnReport = report.items
        total = report.total
        if report.iter_pages():
            pages=0
        else:
            pages = max(report.iter_pages())
        tableData = []
        for item in returnReport:
            reportData = item.to_dict()
            tableData.append(reportData)
        if tableData:
            return jsonify({'code': '200', 'errmsg': '查询成功！', 'total':total,'pages':pages,"tableData": tableData})
        else:
            return jsonify({'code': '200', 'errmsg': '查询结果为空！'})
    elif reportName != '' and reportStatus == '' and creatDate == '':
        report = ReportResult.query.filter_by(reportName=reportName).paginate(page, per_page, error_out=False)
        returnReport = report.items
        total = report.total
        if report.iter_pages():
            pages=0
        else:
            pages = max(report.iter_pages())
        tableData = []
        for item in returnReport:
            reportData = item.to_dict()
            tableData.append(reportData)
        if tableData:
            return jsonify({'code': '200', 'errmsg': '查询成功！', 'total':total,'pages':pages,"tableData": tableData})
        else:
            return jsonify({'code': '200', 'errmsg': '查询结果为空！'})
    elif reportName == '' and reportStatus != '' and creatDate != '':
        report = ReportResult.query.filter(ReportResult.reportStatus.in_(reportStatus),ReportResult.creatDate.like("%" + creatDate + "%")).paginate(page, per_page, error_out=False)
        returnReport = report.items
        total = report.total
        if report.iter_pages():
            pages=0
        else:
            pages = max(report.iter_pages())
        tableData = []
        for item in returnReport:
            reportData = item.to_dict()
            tableData.append(reportData)
        if tableData:
            return jsonify({'code': '200', 'errmsg': '查询成功！', 'total':total,'pages':pages,"tableData": tableData})
        else:
            return jsonify({'code': '200', 'errmsg': '查询结果为空！'})
    elif reportName == '' and reportStatus != '' and creatDate == '':
        report = ReportResult.query.filter(ReportResult.reportStatus.in_(reportStatus)).paginate(page, per_page, error_out=False)
        returnReport = report.items
        total = report.total
        if report.iter_pages():
            pages=0
        else:
            pages = max(report.iter_pages())
        tableData = []
        for item in returnReport:
            reportData = item.to_dict()
            tableData.append(reportData)
        if tableData:
            return jsonify({'code': '200', 'errmsg': '查询成功！', 'total':total,'pages':pages,"tableData": tableData})
        else:
            return jsonify({'code': '200', 'errmsg': '查询结果为空！'})
    elif reportName == '' and reportStatus == '' and creatDate != '':
        report = ReportResult.query.filter(ReportResult.creatDate.like("%" + creatDate + "%")).paginate(page, per_page, error_out=False)
        returnReport = report.items
        total = report.total
        if report.iter_pages():
            pages=0
        else:
            pages = max(report.iter_pages())
        tableData = []
        for item in returnReport:
            reportData = item.to_dict()
            tableData.append(reportData)
        if tableData:
            return jsonify({'code': '200', 'errmsg': '查询成功！', 'total':total,'pages':pages,"tableData": tableData})
        else:
            return jsonify({'code': '200', 'errmsg': '查询结果为空！'})
    else:
        return jsonify({'status': '200', 'errmsg': '查询结果为空！'})







@testreport.route('/getReport',methods=['POST'])
def getReport():
    '''
    详情页获取报告信息接口，用于展示头部统计信息
    :return:
    '''
    id = request.form.get('reportId')
    report = ReportResult.query.filter_by(id=id).all()
    tableData = []
    for item in report:
        reportData = item.to_dict()
        tableData.append(reportData)
    if tableData == '':
        return jsonify({'code': '200', 'errmsg': '查询结果为空！'})
    else:
        return jsonify({'code': '200', 'errmsg': '查询成功！', "tableData": tableData})





@testreport.route('/caseDetails',methods=['POST'])
def caseDetails():
    '''
    详情页获取case信息接口，用于展示列表详细信息
    :return:
    '''
    taskId = request.form.get('taskId')
    caseResult = CaseResult.query.filter_by(caseTask=taskId).all()
    caseData = []
    for item in caseResult:
        case = item.to_dict()
        caseId = case['caseId']
        caseName = Testcase.query.filter_by(id=caseId).first().to_dict()['caseName']
        case['caseName']=caseName
        caseData.append(case)
    if caseData == '':
        return jsonify({'code': '200', 'errmsg': '查询结果为空！'})
    else:
        return jsonify({'code': '200', 'errmsg': '查询成功！', "caseData": caseData})


@testreport.route('/jinmu',methods=['POST'])
def jinmuTest():
    yml2testcase('E:/git/Git/RhinoPlatform/app/testreport/index.yml')
    return jsonify({'errmsg':'请求成功'})


