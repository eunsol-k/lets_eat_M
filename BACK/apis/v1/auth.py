from flask import jsonify, make_response
from services.CRUDUser import CRUDUser
from MODEL.base_classes import User
from http import HTTPStatus
from flask_restx import Resource, Namespace, fields, reqparse
from app import rc
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import bcrypt

crudUser = CRUDUser()


Auth = Namespace(
    name='Auth',
    description='사용자 인증을 위한 API'
)


resource_parser = reqparse.RequestParser()
refresh_parser = reqparse.RequestParser()

resource_parser.add_argument(
    "Authorization", help="Bearer {access_token}", type=str, required=True, location="headers", default="Bearer ")
refresh_parser.add_argument(
    "Authorization", help="Bearer {refresh_token}", type=str, required=True, location="headers", default="Bearer ")


token_req_model = Auth.model(name="토큰 발급 요청 모델", model={
    "id": fields.String(required=True, description="사용자 아이디"),
    "pw": fields.String(required=True, description="사용자 비밀번호")
})

users_register_model = Auth.inherit('사용자 회원 가입 요청 모델', token_req_model, {
    'username': fields.String(description='사용자 이름', required=True)
})

token_res_model = Auth.model(name="토큰 발급 응답 모델", model={
    "access_token": fields.String(description="액세스 토큰"),
    "refresh_token": fields.String(description="재발급 토큰")
})

token_patch_model = Auth.model(name="토큰 갱신 응답 모델", model={
    "access_token": fields.String(description="액세스 토큰")
})

user_model = Auth.model(name="사용자 모델", model={
    "id": fields.String(description="사용자 아이디"),
    "pw": fields.String(description="사용자 비밀번호"),
    "username": fields.String(description="사용자 이름"),
    "expired_date": fields.DateTime(description="회원 탈퇴 일자")
})

error_message = Auth.model(name="오류 메시지 모델", model={
    "msg": fields.String(description="오류 내용")
})


@Auth.route('/register')
class UsersRegister(Resource):
    @Auth.doc(description="""회원 가입 시 사용하는 API입니다.\n토큰을 발급하지 않습니다.""")
    @Auth.expect(users_register_model)
    @Auth.response(HTTPStatus.CREATED.value, '회원 가입 성공.')
    @Auth.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, '이미 존재하는 유저입니다.', error_message)
    def post(self):
        """회원 가입"""
        args = Users.payload
        user_id = args.get('id')
        user_pw = args.get('pw')
        user_name = args.get('username')
        encoded_pw = bcrypt.hashpw(user_pw.encode("utf-8"), bcrypt.gensalt())

        user = User(user_id, encoded_pw, user_name)
        result = crudUser.set(user=user)

        if result:
            return "", HTTPStatus.CREATED.value
        else:
            return make_response(jsonify(msg='User already Exists.'), HTTPStatus.INTERNAL_SERVER_ERROR.value)


@Auth.route("/tokens")
class Token(Resource):
    @Auth.doc(description="""JWT 토큰을 발급하는 API입니다.\n로그인과 같은 기능입니다.""")
    @Auth.expect(token_req_model)
    @Auth.marshal_with(fields=token_res_model, code=HTTPStatus.CREATED.value, description="토큰 발급 성공.")
    @Auth.response(HTTPStatus.UNAUTHORIZED.value, '인증되지 않은 사용자입니다.', error_message)
    def post(self):
        """토큰 발급"""

        args = Auth.payload
        user_id = args.get('id')
        user_pw = args.get('pw')
        user = crudUser.get(user_id=user_id)

        if crudUser.is_exists_by_id(user_id) and crudUser.is_correct(user_id=user_id, user_pw=bcrypt.hashpw(user_pw.encode("utf-8"), bcrypt.gensalt())):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            return dict(access_token=access_token, refresh_token=refresh_token), HTTPStatus.CREATED.value

        return make_response(jsonify(msg="Unauthorized."), HTTPStatus.UNAUTHORIZED.value)


    @Auth.doc(description="""인증 토큰을 갱신하는 API입니다.""")
    @Auth.expect(refresh_parser)
    @Auth.marshal_with(fields=token_patch_model, code=HTTPStatus.CREATED.value, description='토큰 갱신 성공.')
    @jwt_required(refresh=True)
    def patch(self):
        """토큰 갱신"""

        access_token = create_access_token(identity=get_jwt_identity())
        return dict(access_token=access_token), HTTPStatus.CREATED.value


    @Auth.doc(description="""인증 토큰을 폐기하는 API입니다.\n로그아웃과 같은 기능으로 인증 토큰을 폐기하고 재사용을 방지합니다.""")
    @Auth.expect(resource_parser)
    @Auth.response(code=HTTPStatus.NO_CONTENT.value, description="토큰이 성공적으로 폐기되었을 때 반환.")
    @jwt_required()
    def delete(self):
        """토큰 폐기"""
        crudUser.update_expired_date(user_id=get_jwt_identity())

        rc.set(name=get_jwt().get("jti"), value="")
        return "", HTTPStatus.NO_CONTENT.value


@Auth.route("/users")
class Users(Resource):
    @Auth.doc(description="""사용자를 조회하는 API입니다.""")
    @Auth.expect(resource_parser)
    @Auth.marshal_with(fields=user_model, as_list=True, code=HTTPStatus.OK.value, description="사용자 조회 성공.")
    @jwt_required()
    def get(self):
        """사용자 조회"""

        user = crudUser.get(user_id=get_jwt_identity())
        user = user.serialize()
        return user, HTTPStatus.OK.value