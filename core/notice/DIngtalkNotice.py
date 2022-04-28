"""
@File: DIngtalkNotice.py
@author: guoweiliang
@date: 2021/4/13
"""
from typing import List, Dict

from dingtalkchatbot.chatbot import DingtalkChatbot
from config import Config


def sendMsg(title, msg, *atMobile):
    webhook = Config.Dingtalk_access_token
    msgSend = DingtalkChatbot(webhook)
    msgSend.send_markdown(title=title, text=msg, at_mobiles=atMobile)


def taskResultInfo(taskName):
    """
    任务执行完成之后通知到钉钉群内
    失败case 艾特到人
    :return: 用例信息 字典类型
    """
    pass


def dailyJobResultNotice() -> None:
    """
    每天定时任务执行结果 通知到钉钉群
    失败case 艾特到人
    :return:
    """
    pass


def constructDingMsg():
    """
    构造钉钉通知消息
    :return:
    """


def main(projectName):
    authorFailedCase = {"杨无邪": ["测试登录", "测试数据权限"], "金木": ["企团险对接流程"]}
    ddContent = f"""#### 项目名: {projectName} \n#### 项目分支: test_using \n> | 创建人 | 失败用例 |\n| :----- | :----- |\n"""
    for key, value in authorFailedCase.items():
        ddContent += f"{key} &nbsp; &nbsp; &nbsp; &nbsp; | {value} \n"
    sendMsg(title=projectName + "test_using执行报告", msg=ddContent)


if __name__ == '__main__':
    ddCtent = """#### 项目名: debug \n#### 项目分支: test_using \n> | 创建人 |&nbsp; &nbsp; &nbsp; &nbsp;  失败用例 |\n| :----: | :----: |\n
    | 张三 | &nbsp; &nbsp; &nbsp; &nbsp;  ['喂小保后台-代理人认证-列表初始化查询', '喂小保后台-代理人认证-一键同步信息到核心系统', '喂小保后台-banner管理-撤销banner', '喂小保后台-入职审核-页面初始化信息查询', '喂小保后台-入职审核-入职人员详情信息查看', '喂小保后台-获客渠道配置-列表初始化查询', '喂小保后台-获客渠道配置-编辑获客渠道配置', '喂小保后台-险企账号管理-列表初始化查询', '喂小保后台-险企账号管理-新增险企账号', '喂小保后台-险企账号管理-停用险企账号', '喂小保后台-险企账号管理-启用险企账号', '喂小保后台-险企账号管理-批量启用险企账号', '喂小保后台-消息中心-创建消息,立即发送', '喂小保后台-团险订单管理-订单详情', '喂小保后台-公众号自动回复-列表初始化查询', '喂小保后台-公众号自动回复-发布话术规则', '喂小保后台-公众号自动回复-停用话术规则', '喂小保后台-公众号数据统计-数据信息查询', '喂小保后台-公众号粉丝-列表初始化查询', '喂小保后台-公众号粉丝-查看粉丝数据详情', '喂小保后台-公众号粉丝-粉丝数据导出', '喂小保后台-投放数据漏斗-导出', '喂小保后台-公众号数据统计-导出数据', '喂小保后台-规划师一览-规划师详情'] | \n
    | 李四 | &nbsp; &nbsp; &nbsp; &nbsp;  ['喂小保后台佣金配置'] | \n
    | 王五 | &nbsp; &nbsp; &nbsp; &nbsp;  ['喂小保后台-订单管理-订单查询-初始化config', '喂小保后台_订单查询_list接口', '喂小保后台_订单查询_orgRankList接口', '喂小保后台_订单查询_list接口多条件', '喂小保后台_订单查询_订单详情_detail接口'] | \n
    """
    sendMsg(title="test执行报告", msg=ddCtent)
