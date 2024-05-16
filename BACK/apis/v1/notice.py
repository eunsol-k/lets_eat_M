from flask import jsonify, make_response
from services.CRUDNotice import CRUDNotice
from services.CRUDUser import CRUDUser
from http import HTTPStatus
from flask_restx import Resource, Namespace, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity


crudNotice = CRUDNotice()
crudUser = CRUDUser()


Notice = Namespace(
    name='Notice',
    description='공지사항 관리 관련 API'
)


resource_parser = reqparse.RequestParser()
resource_parser.add_argument(
    "Authorization", help="Bearer {access_token}", type=str, required=True, location="headers", default="Bearer ")

request_parser = reqparse.RequestParser()
request_parser.add_argument(
    "Authorization", help="Bearer {access_token}", type=str, required=True, location="headers", default="Bearer ")
request_parser.add_argument("title", type=str, location="body")
request_parser.add_argument("body", type=str, location="body")
request_parser.add_argument("fixed", type=bool, location="body")

notice_req_fields = Notice.model('공지사항 추가 요청 모델', {
    'title': fields.String(description='게시물 제목'),
    'body': fields.String(description='게시물 내용'),
    'fixed': fields.Boolean(description='고정 여부')
})

status_message = Notice.model(name="HTTP Status 메시지 모델", model={
    "msg": fields.String(description="Status 내용")
})

notice_fields = Notice.model('공지사항 items 이하 모델', {
    'id': fields.Integer(description='게시물 ID'),
    'title': fields.String(description='게시물 제목'),
    'hits': fields.Integer(description='조회수'),
    'fixed': fields.Boolean(description='고정 여부'),
})

notice_all_res_fields = Notice.model('통상 응답 모델', {
    'totalCount': fields.Integer(description='item 총 개수'),
    'items': fields.List(fields.Nested(notice_fields))
})

notice_res_fields = Notice.inherit('공지사항 단일 조회 응답 모델', notice_fields, {
    'body': fields.String(description='게시물 내용'),
    'created_date': fields.String(description='게시물 생성일자'),
    'modified_date': fields.String(description='게시물 수정일자')
})

resource_parser = reqparse.RequestParser()
resource_parser.add_argument(
    "Authorization", help="Bearer {access_token}", type=str, required=True, location="headers", default="Bearer ")


@Notice.route("")
class Notices(Resource):
    @Notice.doc(description="""공지사항 전체 목록을 불러옵니다.""")
    @Notice.response(HTTPStatus.OK.value, '공지사항 목록 조회 성공.', notice_all_res_fields)
    def get(self):
        """공지사항 전체 목록 조회"""
        notices = crudNotice.get_all()

        items = []
        data = {
            'totalCount': len(notices),
            'items': items
        }

        if notices is None or len(notices) == 0:
            data['totalCount'] = 0
        else:
            for notice in notices:
                item = {
                    'notice_id': notice.id,
                    'title': notice.title,
                    'hits': notice.hits,
                    'fixed': notice.fixed
                }
                items.append(item)

        return make_response(data, HTTPStatus.OK.value)

    @Notice.doc(description="""공지사항을 추가합니다.""")
    @Notice.expect(request_parser)
    @Notice.response(HTTPStatus.CREATED.value, '게시물 추가 성공.', status_message)
    @Notice.response(HTTPStatus.UNAUTHORIZED.value, '관리자가 아닙니다.', status_message)
    @jwt_required()
    def post(self):
        """공지사항 추가"""
        admin = crudUser.get(user_id=get_jwt_identity())
        if admin.role != 'ADMIN':
            return make_response(jsonify(msg="Unauthorized."), HTTPStatus.UNAUTHORIZED.value)
        
        args = Notice.payload
        title = args.get('title')
        body = args.get('body')
        fixed = args.get('fixed')

        crudNotice.set(title=title, body=body, fixed=fixed)
        return make_response(jsonify(msg="Added Notice."), HTTPStatus.CREATED.value)


@Notice.route("/<notice_id>")
class NoticesWithID(Resource):
    @Notice.doc(description="""notice_id에 해당하는 공지사항을 조회합니다.""")
    @Notice.response(HTTPStatus.OK.value, '게시물 조회 성공.', notice_res_fields)
    def get(self, notice_id):
        """공지사항 단일 게시물 조회"""
        notice = crudNotice.get(notice_id=notice_id)
        notice_dict = vars(notice)
        del notice_dict['_sa_instance_state']

        return notice_dict, HTTPStatus.OK.value

    @Notice.doc(description="""공지사항을 수정합니다.""")
    @Notice.expect(request_parser)
    @Notice.response(HTTPStatus.OK.value, '공지사항 수정 성공.', status_message)
    @Notice.response(HTTPStatus.UNAUTHORIZED.value, '관리자가 아닙니다.', status_message)
    @jwt_required()
    def patch(self, notice_id):
        """공지사항 수정"""
        admin = crudUser.get(user_id=get_jwt_identity())
        if admin.role != 'ADMIN':
            return make_response(jsonify(msg="Unauthorized."), HTTPStatus.UNAUTHORIZED.value)

        args = Notice.payload
        title = args.get('title')
        body = args.get('body')
        fixed = args.get('fixed')

        crudNotice.update(notice_id=notice_id, title=title, body=body, fixed=fixed)
        return make_response(jsonify(msg="Updated Notice."), HTTPStatus.OK.value)

    @Notice.doc(description="""공지사항을 삭제합니다.""")
    @Notice.expect(resource_parser)
    @Notice.response(HTTPStatus.NO_CONTENT.value, '공지사항 삭제 성공.', status_message)
    @Notice.response(HTTPStatus.UNAUTHORIZED.value, '관리자가 아닙니다.', status_message)
    @jwt_required()
    def delete(self, notice_id):
        """공지사항 삭제"""
        admin = crudUser.get(user_id=get_jwt_identity())
        if admin.role != 'ADMIN':
            return make_response(jsonify(msg="Unauthorized."), HTTPStatus.UNAUTHORIZED.value)

        crudNotice.delete(notice_id=notice_id)
        return make_response(jsonify(msg="Deleted Notice."), HTTPStatus.NO_CONTENT.value)
