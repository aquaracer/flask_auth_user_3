from flask import Flask, jsonify, request
from app import controller, models
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import config
from const import HTTP_OK, HTTP_BAD_REQUEST, HTTP_NOT_FOUND

app = Flask(__name__)
app.debug = config.DevelopementConfig.DEBUG

@app.route('/')
def hello_world():
    return 'Welcome to User Authorization Page!'


@app.route('/users/<int:page_number>/<int:page_size>', methods=['GET'])
def users_list(page_number:int, page_size:int):
    result = {}
    code = HTTP_OK
    try:
        final_list = controller.list_of_users(page_number, page_size)
        result['data'] = final_list
    except Exception as e:
        result['error']=repr(e)
        print(result) # выводим лог в stdout
        code = HTTP_BAD_REQUEST
    return jsonify(result), code


@app.route('/user', methods=['POST'])
def user_registration():
    json = request.get_json() # получаем json из POST запроса
    login = json['login']
    password = json['password']
    admin = json['admin']
    expiration_date = json['expiration_date']
    result = {}
    code = HTTP_OK
    try:
        controller.registration(login, password, admin, expiration_date) # пытаемся зарегистрировать пользователя
        result['data'] = 'new user has been registered successfully'
    except Exception as e:
        result['error'] = repr(e)
        print(result) # выводим лог в stdout
        code = HTTP_BAD_REQUEST
    return jsonify(result), code


@app.route('/user/<int:id>', methods=['GET'])
def get_user_id(id:int):
    result = {}
    code = HTTP_OK
    try:
        login = controller.get_user_info(id)  # пытаемся получить информацию о пользователе по ID
        result['data'] = login
    except Exception as e:
        result['error'] = repr(e)
        print(result)  # выводим лог в stdout
        code = HTTP_NOT_FOUND
    return jsonify(result), code


@app.route('/user', methods=['DELETE'])
def delete_info():
    json = request.get_json(force=True)
    user_id = json['user_id']
    result = {}
    code = HTTP_OK
    try:
        report = controller.delete_user(user_id)  # пытаемся удалить информацию о пользователе по ID
        result['data'] = report
    except Exception as e:
        result['error'] = repr(e)
        print(result)  # выводим лог в stdout
        code = HTTP_BAD_REQUEST
    return jsonify(result), code


@app.route('/user', methods=['PATCH'])
def update_info():
    json = request.get_json(force=True)
    user_id = json['user_id']
    password = json['password']
    result = {}
    code = HTTP_OK
    try:
        report = controller.update_user(user_id, password)  # пытаемся удалить информацию о пользователе по ID
        result['data'] = report
    except Exception as e:
        result['error'] = repr(e)
        print(result)  # выводим лог в stdout
        code = HTTP_BAD_REQUEST
    return jsonify(result), code


@app.route('/login', methods=['POST'])
def user_auth():
    json = request.get_json(force=True)
    login = json['login']
    password = json['password']
    result = {}
    code = HTTP_OK
    try:
        token = controller.auth(login, password)  # пытаемся пройти аутентификацию и получить JWT токен
        result['data'] = str(token)
    except Exception as e:
        result['error'] = repr(e)
        print(result)  # выводим лог в stdout
        code = HTTP_NOT_FOUND
    return jsonify(result), code


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()