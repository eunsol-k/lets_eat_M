from flask import jsonify, make_response
from services.CRUDHistory import CRUDHistory
from services.CRUDMedicine import CRUDMedicine
from services.CRUDInterest import CRUDInterest
from http import HTTPStatus
from flask_restx import Resource, Namespace, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity


crudHistory = CRUDHistory()
crudMedicine = CRUDMedicine()
crudInterest = CRUDInterest()


History = Namespace(
    name='History',
    description='제품 조회 기록을 위한 API'
)


resource_parser = reqparse.RequestParser()
resource_parser.add_argument(
    "Authorization", help="Bearer {access_token}", type=str, required=True, location="headers", default="Bearer ")

status_message = History.model(name="HTTP Status 메시지 모델", model={
    "msg": fields.String(description="Status 내용")
})

histories_fields = History.model('조회 기록 items 이하 모델', {
    'history_id': fields.Integer(description='조회 기록 ID'),
    'item_id': fields.String(description='제품 ID'),
    'item_name': fields.String(description='제품명'),
    'item_image': fields.String(description='제품 이미지'),
    'like': fields.Boolean(description='좋아요 여부')
})

histories_res_fields = History.model('통상 응답 모델', {
    'totalCount': fields.Integer(description='item 총 개수'),
    'items': fields.List(fields.Nested(histories_fields))
})


@History.route("")
class HistoryGet(Resource):
    @History.doc(description="""조회 기록 목록을 불러옵니다.""")
    @History.expect(resource_parser)
    @History.response(HTTPStatus.OK.value, '조회 기록 확인 성공.', histories_res_fields)
    @History.response(HTTPStatus.UNAUTHORIZED.value, '인증되지 않은 사용자입니다.', status_message)
    @jwt_required(optional=True)
    def get(self):
        """조회 기록 불러오기"""
        user_id = get_jwt_identity()
        if not user_id:
            # 로그인되어 있지 않은 경우
            return make_response(jsonify(msg="Unauthorized."), HTTPStatus.UNAUTHORIZED.value)
        else:
            # 로그인되어 있는 경우
            # 현재 limit 무조건 10
            histories = crudHistory.get_all_by_user(user_id=user_id)
            items = []
            data = {
                'totalCount': len(histories),
                'items': items
            }

            if histories is None or len(histories) == 0:
                data['totalCount'] = 0
            else:
                for history in histories:
                    medicine = crudMedicine.get(item_id=history.item_id)
                    interest = crudInterest.is_exists(
                        user_id=user_id, item_id=history.item_id)

                    item = {
                        'history_id': history.id,
                        'item_id': history.user_id,
                        'item_name': medicine.item_name,
                        'item_image': medicine.item_image,
                        'like': interest
                    }
                    items.append(item)

            return make_response(data, HTTPStatus.OK.value)


@History.route("/<item_id>")
class HistoryPost(Resource):
    @History.doc(description="""조회 기록을 추가합니다.""")
    @History.expect(resource_parser)
    @History.response(HTTPStatus.CREATED.value, '조회 기록 추가 성공.', status_message)
    @History.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @jwt_required()
    def post(self, item_id):
        """조회 기록 추가"""
        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)

        crudHistory.set(user_id=get_jwt_identity(), item_id=item_id)

        return make_response(jsonify(msg="Added search history."), HTTPStatus.CREATED.value)

    @History.doc(description="""조회 기록을 삭제합니다.""")
    @History.expect(resource_parser)
    @History.response(HTTPStatus.NO_CONTENT.value, '조회 기록 삭제 성공.', status_message)
    @History.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @jwt_required()
    def delete(self, item_id):
        """조회 기록 삭제"""
        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)

        crudHistory.delete(user_id=get_jwt_identity(), item_id=item_id)

        return make_response(jsonify(msg="Deleted search history."), HTTPStatus.NO_CONTENT.value)