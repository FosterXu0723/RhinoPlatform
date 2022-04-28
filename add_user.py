"""
    :author: xiaoyicai.
    :date: 2021/05/08.
"""
from app import db, create_app
# from manage import app
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()


def add_user_byhand():
    with app.app_context():
        user = User()
        user.username = 'xiaoyicai2'
        user.password_hash = generate_password_hash('123456')
        user.operator = '通过脚本添加的'
        db.session.add(user)
        db.session.commit()


if __name__ == '__main__':
    try:
        add_user_byhand()

    except Exception as e:
        raise e
