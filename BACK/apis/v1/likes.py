from flask import jsonify, make_response
from services.CRUDInterest import CRUDInterest
from services.CRUDMedicine import CRUDMedicine
from http import HTTPStatus
from flask_restx import Resource, Namespace, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity


crudInterest = CRUDInterest()
crudMedicine = CRUDMedicine()


Likes = Namespace(
    name='Likes',
    description='좋아요 관련 기능을 제공하는 API'
)


items_fields = Likes.model('좋아요 items 이하 모델', {
    'item_id': fields.String(description='제품 ID'),
    'item_name': fields.String(description='제품명'),
    'item_image': fields.String(description='제품 이미지')
})

likes_res_fields = Likes.model('좋아요 전체 목록 응답 모델', {
    'totalCount': fields.Integer(description='item 총 개수'),
    'items': fields.List(fields.Nested(items_fields))
})

resource_parser = reqparse.RequestParser()
resource_parser.add_argument(
    "Authorization", help="Bearer {access_token}", type=str, required=True, location="headers", default="Bearer ")

status_message = Likes.model(name="HTTP Status 메시지 모델", model={
    "msg": fields.String(description="Status 내용")
})

likes_cdt_res = Likes.model(name="좋아요 상태 확인 요청 모델", model={
    "is_liked": fields.Boolean(description="좋아요 여부")
})


@Likes.route('')
class Like(Resource):
    @Likes.doc(description="""좋아요 전체 목록을 불러옵니다.""")
    @Likes.expect(resource_parser)
    @Likes.response(HTTPStatus.OK.value, '좋아요 전체 목록 조회 성공.', likes_res_fields)
    @jwt_required()
    def get(self):
        """좋아요 전체 목록 조회"""
        likes = crudInterest.get_all_by_user(user_id=get_jwt_identity())
        items = []
        data = {
            'totalCount': len(likes),
            'items': items
        }

        if likes is None or len(likes) == 0:
            data['totalCount'] = 0
        else:
            for like in likes:
                item_id = like.item_id
                medicine = crudMedicine.get(item_id=item_id)
                item = {
                    'item_id': medicine.item_id,
                    'item_name': medicine.item_name,
                    'item_image': medicine.item_image
                }
                items.append(item)

        return make_response(data, HTTPStatus.OK.value)


@Likes.route('/<item_id>')
class LikesItem(Resource):
    @Likes.doc(description="""item_id에 해당하는 특정 제품을 좋아요 처리합니다.""")
    @Likes.expect(resource_parser)
    @Likes.response(HTTPStatus.OK.value, '제품 좋아요 ON/OFF 성공.', status_message)
    @Likes.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @jwt_required()
    def post(self, item_id):
        """제품 좋아요 상태 갱신"""
        user_id = get_jwt_identity()

        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)
        else:
            is_exists = crudInterest.is_exists(
                user_id=user_id, item_id=item_id)
            if is_exists:
                crudInterest.off(user_id=user_id, item_id=item_id)
                return make_response(jsonify(msg="Like Off."), HTTPStatus.OK.value)
            else:
                crudInterest.on(user_id=user_id, item_id=item_id)
                return make_response(jsonify(msg="Like On."), HTTPStatus.OK.value)

    @Likes.doc(description="""item_id에 해당하는 특정 제품의 좋아요 표시 여부를 확인합니다.""")
    @Likes.expect(resource_parser)
    @Likes.response(HTTPStatus.OK.value, '제품 좋아요 상태 확인 성공.', likes_cdt_res)
    @Likes.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @jwt_required()
    def get(self, item_id):
        """제품 좋아요 상태 조회"""
        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)
        else:
            is_liked = crudInterest.is_exists(
                user_id=get_jwt_identity(), item_id=item_id)
            return make_response(jsonify(is_liked=is_liked), HTTPStatus.OK.value)
