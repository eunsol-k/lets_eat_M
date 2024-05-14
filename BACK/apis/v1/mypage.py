from flask import jsonify, make_response
from services.CRUDUser import CRUDUser
from services.CRUDInterest import CRUDInterest
from services.CRUDMedicine import CRUDMedicine
from http import HTTPStatus
from flask_restx import Resource, Namespace, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity


crudUser = CRUDUser()
crudInterest = CRUDInterest()
crudMedicine = CRUDMedicine()


MyPage = Namespace(
    name='MyPage',
    description='마이페이지 관련 기능을 제공하는 API'
)


items_fields = MyPage.model('items 이하 모델', {
    'item_id': fields.String(description='제품 ID'),
    'item_img': fields.String(description='제품 이미지')
})

likes_res_fields = MyPage.model('좋아요 목록 응답 모델', {
    'count': fields.Integer(description='좋아요 물품들 총 갯수'),
    'items': fields.List(fields.Nested(items_fields))
})

resource_parser = reqparse.RequestParser()
resource_parser.add_argument(
    "Authorization", help="Bearer {access_token}", type=str, required=True, location="headers", default="Bearer ")

request_parser = reqparse.RequestParser()
request_parser.add_argument(
    "Authorization", help="Bearer {access_token}", type=str, required=True, location="headers", default="Bearer ")
request_parser.add_argument(
    "item_id", type=str, required=True, location="body")

status_message = MyPage.model(name="HTTP Status 메시지 모델", model={
    "msg": fields.String(description="Status 내용")
})


@MyPage.route('/likes')
class Likes(Resource):
    @MyPage.doc(description="""item_id에 해당하는 특정 제품을 관심 처리합니다.""")
    @MyPage.expect(request_parser)
    @MyPage.response(HTTPStatus.OK.value, '제품 좋아요 ON/OFF 성공.', status_message)
    @MyPage.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @MyPage.response(HTTPStatus.BAD_REQUEST.value, '양식에 맞지 않는 요청입니다.', status_message)
    @jwt_required
    def post(self):
        """관심 제품 갱신"""
        args = MyPage.payload
        item_id = args.get('item_id')
        user_id = get_jwt_identity()

        if not isinstance(item_id, int):
            return make_response(jsonify(msg="Bad Request."), HTTPStatus.BAD_REQUEST.value)
        elif not crudMedicine.is_exists(item_id=item_id):
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

    @MyPage.doc(description="""관심 전체 목록을 불러옵니다.""")
    @MyPage.expect(resource_parser)
    @MyPage.response(HTTPStatus.OK.value, '전체 목록 조회 성공.', likes_res_fields)
    @jwt_required
    def get(self):
        """관심 목록 조회"""
        likes = crudInterest.get_all_by_user(user_id=get_jwt_identity())
        items = []
        data = {
            'count': len(likes),
            'items': items
        }

        if likes is None or len(likes) == 0:
            data['count'] = 0
        else:
            for like in likes:
                item_id = like.item_id
                medicine = crudMedicine.get(item_id=item_id)
                item = {
                    'item_id': medicine.item_id,
                    'item_img': medicine.product_img
                }
                items.append(item)

        return make_response(jsonify(data=data), HTTPStatus.OK.value)
