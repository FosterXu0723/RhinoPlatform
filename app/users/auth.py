# 作者       ：yangwuxie
# 创建时间   ：2020/11/25 15:41

from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from app.users.errors import error_response
from config import Config

auth_token = HTTPTokenAuth()


@auth_token.verify_token
def verify_token(token):
    s = Serializer(Config.SECRET_KEY)
    try:
        data = s.loads(token)
    except BadSignature:
        # AuthFailed 自定义的异常类型
        return False
    except SignatureExpired:
        return False
    # 校验通过返回True
    return data


@auth_token.error_handler
def token_auth_error():
    return error_response(200, "token expired")


if __name__ == '__main__':
    print(verify_token('eyJhbGciOiJIUzUxMiIsImlhdCI6MTYwODU1OTg4OSwiZXhwIjoxNjA4NTYzNDg5fQ.eyJpZCI6MX0.KqdQJBSoltZ7x6GmE-FYSRodfFnDldVZIPrqUXUi4QuyPSInDtP9GGSKvXqziPiO05WJwYcwZCUfjJnz-ZV-ZQ'))