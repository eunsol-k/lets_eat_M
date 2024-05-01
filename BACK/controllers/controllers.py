from flask import Blueprint, jsonify, request
from MODEL.base_classes import User
from services.CRUDUser import CRUDUser
from services.CRUDInterest import CRUDInterest
from services.CRUDMedicine import CRUDMedicine
from http import HTTPStatus


crudUser = CRUDUser()
crudInterest = CRUDInterest()
crudMedicine = CRUDMedicine()
STATUS = {}

rt_bp = Blueprint(name='root', import_name=__name__, url_prefix='/')

def non_exist_msg(msg):
    STATUS['code'] = HTTPStatus.BAD_REQUEST
    STATUS['msg'] = f'non-existent {msg}.'

def invalid_type_msg(msg):
    STATUS['code'] = HTTPStatus.BAD_REQUEST
    STATUS['msg'] = f'Invalid type of {msg}.'

@rt_bp.route('/')
def root():
    return "hello world!"

@rt_bp.route('/signup', methods=['POST'])
def signup() -> str:
    data = request.get_json()
    user = User(data['id'], data['pw'], data['username'])
    result = crudUser.set(user=user)

    if result:
        STATUS['code'] = HTTPStatus.CREATED
        STATUS['msg'] = 'user created.'
    else:
        STATUS['code'] = HTTPStatus.ACCEPTED
        STATUS['msg'] = 'user already exists.'

    return jsonify(status=STATUS), STATUS['code']


@rt_bp.route('/withdraw', methods=['DELETE'])
def withdraw():
    data = request.get_json()
    user_id = data['id']
    user_pw = data['pw']

    if not crudUser.is_correct(user_id=user_id, user_pw=user_pw):
        non_exist_msg('user')
    elif crudUser.is_expired(user_id=user_id):
        STATUS['code'] = HTTPStatus.ACCEPTED
        STATUS['msg'] = 'already expired user.'
    else:
        crudUser.update_expired_date(user_id=user_id)
        STATUS['code'] = HTTPStatus.OK
        STATUS['msg'] = 'user expired.'
    
    return jsonify(status=STATUS), STATUS['code']


@rt_bp.route('/like', methods=['POST'])
def like_on_off():
    data = request.get_json()
    user_id = data['user_id']
    item_id = data['item_id']

    if not crudUser.is_exists_by_id(user_id=user_id):
        non_exist_msg('user')
    elif not isinstance(item_id, int):
        invalid_type_msg('item_id')
    elif not crudMedicine.is_exists(item_id=item_id):
        non_exist_msg('item')
    else:
        is_exists = crudInterest.is_exists(user_id=user_id, item_id=item_id)
        if is_exists:
            crudInterest.off(user_id=user_id, item_id=item_id)
            STATUS['code'] = HTTPStatus.OK
            STATUS['msg'] = 'like off.'
        else:
            crudInterest.on(user_id=user_id, item_id=item_id)
            STATUS['code'] = HTTPStatus.OK
            STATUS['msg'] = 'like on.'

    return jsonify(status=STATUS), STATUS['code']


@rt_bp.route('/likes/<user_id>', methods=['GET'])
def set_like(user_id) -> str:
    if not crudUser.is_exists_by_id(user_id=user_id):
        return jsonify(status=non_exist_msg('user')), STATUS['code']

    likes = crudInterest.get_all_by_user(user_id=user_id)
    items = []
    data = {
        'count': len(likes),
        'items': items
    }

    if len(likes) == 0:
        STATUS['code'] = HTTPStatus.NO_CONTENT
        STATUS['msg'] = 'no content.'
        return jsonify(status=STATUS), STATUS['code']
    else:
        for like in likes:
            item_id = like.item_id
            medicine = crudMedicine.get(item_id=item_id)
            item = {
                'item_id': medicine.item_id,
                'item_img': medicine.product_img
            }
            items.append(item)

        STATUS['code'] = HTTPStatus.OK
        STATUS['msg'] = 'like list.'
        return jsonify(data=data, status=STATUS), STATUS['code']