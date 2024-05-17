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
    "username": fields.String(description="사용자 이름"),
    "expired_date": fields.DateTime(description="회원 탈퇴 일자")
})

status_message = Auth.model(name="HTTP Status 메시지 모델", model={
    "msg": fields.String(description="Status 내용")
})


@Auth.route("/tokens")
class AuthToken(Resource):
    @Auth.doc(description="""JWT 토큰을 발급하는 API입니다.\n로그인과 같은 기능입니다.""")
    @Auth.expect(token_req_model)
    @Auth.marshal_with(fields=token_res_model, code=HTTPStatus.CREATED.value, description="토큰 발급 성공.")
    @Auth.response(HTTPStatus.UNAUTHORIZED.value, '인증되지 않은 사용자입니다.', status_message)
    def post(self):
        """토큰 발급"""
        args = Auth.payload
        user_id = args.get('id')
        user_pw = args.get('pw')
        user = crudUser.get(user_id=user_id)

        if crudUser.is_exists_by_id(user_id) and crudUser.is_correct(user_id=user_id, user_pw=user_pw):
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


    jwt_blocklist = set()
    @Auth.doc(description="""인증 토큰을 폐기하는 API입니다.\n로그아웃과 같은 기능으로 인증 토큰을 폐기하고 재사용을 방지합니다.""")
    @Auth.expect(resource_parser)
    @Auth.response(HTTPStatus.NO_CONTENT.value, "토큰이 성공적으로 폐기되었을 때 반환.", status_message)
    @jwt_required()
    def delete(self):
        """토큰 폐기"""
        rc.set(name=get_jwt().get("jti"), value="")
        return make_response(jsonify(msg="Token Expired."), HTTPStatus.NO_CONTENT.value)


@Auth.route("/users")
class AuthUsers(Resource):
    @Auth.doc(description="""사용자를 조회하는 API입니다.""")
    @Auth.expect(resource_parser)
    @Auth.response(HTTPStatus.OK.value, "사용자 조회 성공.", user_model)
    @Auth.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 회원 조회 불가.', status_message)
    @jwt_required()
    def get(self):
        """회원 조회"""
        user = crudUser.get(user_id=get_jwt_identity())
        if not user:
            return make_response(jsonify(msg='Non-existent User.'), HTTPStatus.NOT_FOUND.value)

        user_dict = user.__dict__
        
        del user_dict['_sa_instance_state']
        del user_dict['pw']

        return user_dict, HTTPStatus.OK.value
    
    @Auth.doc(description="""회원 가입 시 사용하는 API입니다.\n이후 토큰 발급 API를 요청하세요.""")
    @Auth.expect(users_register_model)
    @Auth.response(HTTPStatus.CREATED.value, '회원 가입 성공.', status_message)
    @Auth.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, '이미 존재하는 유저입니다.', status_message)
    def post(self):
        """회원 가입"""
        args = Auth.payload
        user_id = args.get('id')
        user_pw = args.get('pw')
        user_name = args.get('username')
        encoded_pw = bcrypt.hashpw(user_pw.encode("utf-8"), bcrypt.gensalt())

        user = User(user_id, encoded_pw, user_name, 'User')
        result = crudUser.set(user=user)

        if result:
            return make_response(jsonify(msg='User Created.'), HTTPStatus.CREATED.value)
        else:
            return make_response(jsonify(msg='User already Exists.'), HTTPStatus.INTERNAL_SERVER_ERROR.value)
    
    @Auth.doc(description="""회원 탈퇴 시 사용하는 API입니다.\n이후 토큰 폐기 API를 요청하세요.""")
    @Auth.expect(resource_parser)
    @Auth.response(HTTPStatus.NO_CONTENT.value, "사용자가 성공적으로 탈퇴하였을 때 반환.", status_message)
    @jwt_required()
    def delete(self):
        """회원 탈퇴"""
        crudUser.delete(user_id=get_jwt_identity())
        return make_response(jsonify(msg="User Expired."), HTTPStatus.NO_CONTENT.value)