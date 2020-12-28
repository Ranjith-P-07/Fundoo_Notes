import datetime

import jwt
from Fundoo.settings import SECRET_KEY


def token_activation(username, password):
    """
    :param username: takes user name as parameter
    :param password: takes password
    :return: will return token
    """

    data = {
        'username': username,
        'password': password,
        'exp': datetime.datetime.now()+datetime.timedelta(days=2)
    }
    token = jwt.encode(data, SECRET_KEY, algorithm="HS256").decode('utf-8')
    return token