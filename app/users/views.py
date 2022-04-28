# 作者       ：yangwuxie
# 创建时间   ：2020/11/25 14:28
import datetime
import random
import string

from flask import request, jsonify, session, abort, g, current_app
from sqlalchemy import and_, or_
from app.users.auth import auth_token
from app import db
from app.models import User
from app.users import user


@user.route('/')
@user.route('/login', methods=['POST'], endpoint='login')
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"code": 99999, "msg": "用户不存在"})
    if not user.check_password(password):
        return jsonify({"code": 99999, "msg": "密码错误"})
    token = User.create_token(user.id)
    session['username'] = username
    return jsonify({"code": 10000, "msg": "login success", "token": token})


@user.route('/getUsers', methods=['GET', 'POST'])
@auth_token.login_required
def getAllUser():
    page = int(request.form.get('page'))
    pageSize = int(request.form.get('pageSize'))
    users = User.query.filter(User.delete_status == 1).offset((page - 1) * pageSize).limit(pageSize).all()
    total = len(User.query.filter(User.delete_status == 1).all())
    if len(users) == 0:
        return jsonify({'code': '99999', 'msg': '当前没有用户！'})
    data = {}
    userDataList = []
    for user in users:
        userDataList.append(user.to_dict())
    # 必须返回dict类型
    data['list'] = userDataList
    return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': total})


@user.route('/addUser', methods=['POST'])
@auth_token.login_required
def addUser():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or username == "" or not password or password == "":
        abort(400)
    allUsers = User.query.all()
    if username in list(map(lambda x: x.username, allUsers)):
        return jsonify({
            "code": 99999,
            "msg": "已存在相同用户，请修改用户名重新提交"
        })
    user = User(username=username)
    user.set_password(password)
    # 执行人写入数据库
    user.operator = User.query.filter_by(id=g.flask_httpauth_user.get('id')).first().username
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'code': 10000,
        'msg': '新增用户成功',
        'data': user.to_dict()
    })


@user.route('/getUser', methods=['POST'])
@auth_token.login_required
def getUser():
    """
    {
      "code": 10000,
      "data": {
        "list": [
          {
            "id": 1,
            "username": "admin"
          },
          {
            "id": 2,
            "username": "neil"
          }
        ]
      },
      "msg": "success"
    }
    统一数据格式返回
    :return:
    """
    data = {}
    userDataList = []
    username = request.form.get('username')
    allUsers = User.query.filter(User.delete_status == 1).all()  # 只查询正常状态的用户
    if username == '':
        data['list'] = list(map(lambda x: x.to_dict(), allUsers))
        return jsonify({
            'code': 10000,
            'msg': 'success',
            'data': data
        })
    if username not in list(map(lambda x: x.username, allUsers)):
        return jsonify({
            'code': 99999,
            'msg': '查询用户不存在'
        })
    user = User.query.filter(and_(User.username == username, User.delete_status == 1)).first()
    userDataList.append(user.to_dict())
    data['list'] = userDataList
    return jsonify({
        'code': 10000,
        'msg': 'success',
        'data': data
    })


@user.route('/editUser', methods=['POST'])
@auth_token.login_required
def editUser():
    userId = request.form.get('id')
    username = request.form.get('username')
    password = request.form.get('password')
    passwodcheck = request.form.get('passwordcheck')
    if username == "" or password == "" or passwodcheck == "":
        return jsonify({
            'code': 99999,
            'msg': '用户名或密码不能为空'
        })
    user = User.query.filter(or_(User.id == userId, User.username == username)).first()
    if not user:
        return jsonify({
            'code': 99999,
            'msg': '用户不存在'
        })
    if password != passwodcheck:
        return jsonify({
            'code': 99999,
            'msg': '两次输入密码不一致'
        })
    user.username = username
    user.operator = User.query.filter_by(id=g.flask_httpauth_user.get('id')).first().username
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'code': 10000,
        'msg': '编辑成功'
    })


@user.route('/deleteUser', methods=['POST'])
@auth_token.login_required
def deleteUser():
    userId = request.form.get('id')
    user = User.query.filter(and_(User.id == userId, User.delete_status == 1)).first()
    if not user:
        return jsonify({
            'code': 99999,
            'msg': '该用户未找到'
        })
    if user.username == 'admin':
        return jsonify({
            'code': 99999,
            'msg': '管理员账户禁止删除'
        })
    user.delete_status = 2
    user.operator = session.get('username')
    user.delete_at = datetime.datetime.now()
    db.session.add(user)
    db.session.commit()
    return jsonify({
        "code": 10000,
        'msg': '删除成功'
    })


@user.route("/adminUser", methods=["post"])
def init_admin_user():
    params = request.form
    admin = params.get("username")
    passwd = params.get("password")
    if User.query.filter(User.username == admin).first():
        return jsonify({
            "code": 99999,
            "msg": "已经存在admin用户，无须重复创建！"
        })
    adminUser = User(username=admin)
    adminUser.set_password(passwd)
    try:
        db.session.add(adminUser)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
