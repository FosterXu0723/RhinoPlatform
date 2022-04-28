# 作者       ：yangwuxie
# 创建时间   ：2020/11/26 9:54

login_username_not_message = u"用户名没有输入"
login_password_not_message = u'密码没有输入'
login_user_inactivatesd = u'用户未激活,请联系管理员激活'
login_user_free_message = u'用户冻结！'
login_user_is_login = u'用户已经登录'
login_user_sucess_message = u'登录成功！'
login_user_fremm = u"密码错误超过5次，请十分钟后登录"
login_password_error_message = u'密码错误'
login_user_not_exict_message = u'用户不存在'
activi_user_jobnum = u'用户工号唯一'
activi_user_jobnum_is = u'用户工号已经激活'
interface_add_success = u'添加成功'
interface_add_erroe = u'添加接口失败,请从新添加'
request_null_message = u'没有发送数据'
testeveirment_not_exict = u'没有找到测试环境'
project_not_exict = u'数据库找不到项目'
request_success = u'请求成功'
password_not_same = u'请确认两次密码输入是否一致'
email_geshi_error = u'邮箱格式错误'
jobnum_oblg_reg_one = u'用户工号只能注册一次'
user_exict = u'用户名已经存在'
email_exict = u'邮箱已经注册'
common_is_same = u'通用配置的名称必须唯一'
common_gene_not_support = u'通用配置的类型暂时不支持'
common_is_not_exict = u'编辑的通用配置不存在，请确定'
common_edit_is_success = u'通用配置编辑成功'
re_is_same = u'操作的名称必须唯一'
case_not_exict = u'选择的测试用例不存在'
re_is_not_exitc = u'操作的类型不支持'
re_editisnot = u'编辑操作不存在'
change_password_success = u'修改密码成功'
change_password_error = u'修改密码失败'
user_reset_owner = u'自己不能重置自己的密码'
user_reset_isnot_amin = u'不是管理员不能重置'
user_reset_error = u'重置密码失败'
reset_success_message = u'已经重置！密码：111111'
permiss_is_ness = u'权限不足'
user_is_not_free = u'用户没有处于冻结状态'
activ_is_int = u"工号为数字"
user_is_un_free = u'解冻成功'
ower_not_free_me = u'自己不能解冻自己'
user_is_unfree_success = u'解冻失败'
free_user_error = u'冻结用户失败！'
free_is_success = u'已经冻结成功'
ower_cannot_free_me = u'自己不能冻结自己'
free_is_again = u'已经冻结,无需再次冻结'
admin_cannot_use = u'自己不能取消自己的管理员'

token_expired = 99901


class TransferException(Exception):
    pass


class QueryException(Exception):
    pass


class ApiExtractException(Exception):
    pass


class EnumKeyNotFoundException(Exception):
    """
    枚举类型key未找到异常
    """
    pass


class RequestFailException(Exception):
    """
    自定义请求失败异常
    """
    pass


class ParameterTypeOfDictException(Exception):
    """
    参数不属于字典类型异常
    """
    pass


class JudgeMethodNotAllowedException(Exception):
    """
    断言类型暂不支持异常
    """
    pass


class TaskIdNotSupplyException(Exception):
    """
    未提供task id
    """


class QueryElementNotSupply(Exception):
    """
    sql查询要素未提供完全
    """


class FileTypeNotAllowed(Exception):
    pass
