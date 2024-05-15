from flask import jsonify, make_response
from services.CRUDMedicine import CRUDMedicine
from services.CRUDRating import CRUDRating
from services.CRUDMemo import CRUDMemo
from http import HTTPStatus
from flask_restx import Resource, Namespace, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from configs.config import Config, api_url
import json
import requests


crudMedicine = CRUDMedicine()
crudRating = CRUDRating()
crudMemo = CRUDMemo()


Medicines = Namespace(
    name='Medicine',
    description='의약품 데이터 관련 기능을 제공하는 API'
)


medicine_res_fields = Medicines.model('단일 제품 정보 응답 모델', {
    'item_id': fields.String(description='품목일련번호'),
    'item_name': fields.String(description='품목명'),
    'enter_id': fields.String(description='업소일련번호'),
    'enter_name': fields.String(description='업소명'),
    'constell': fields.String(description='성상'),
    'product_img': fields.String(description='큰제품이미지'),
    'disp_front': fields.String(description='표시앞'),
    'disp_back': fields.String(description='표시뒤'),
    'item_formul': fields.String(description='의약품제형'),
    'color_front': fields.String(description='색상앞'),
    'color_back': fields.String(description='색상뒤'),
    'disv_front': fields.String(description='분할선앞'),
    'disv_back': fields.String(description='분할선뒤'),
    'size_long': fields.String(description='크기장축'),
    'size_short': fields.String(description='크기단축'),
    'size_thick': fields.String(description='크기두께'),
    'creat_date_img': fields.String(description='이미지생성일자(약학정보원)'),
    'class_id': fields.String(description='분류번호'),
    'calss_name': fields.String(description='분류명'),
    'sp_ge': fields.String(description='전문일반구분'),
    'app_date_item': fields.String(description='품목허가일자'),
    'formul_name': fields.String(description='제형코드명'),
    'ind_front_cont': fields.String(description='표기내용앞'),
    'ind_back_cont': fields.String(description='표기내용뒤'),
    'ind_front_img': fields.String(description='표기이미지앞'),
    'ind_back_img': fields.String(description='표기이미지뒤'),
    'ind_front_code': fields.String(description='표기코드앞'),
    'ind_back_code': fields.String(description='표기코드뒤'),
    'modified_date': fields.String(description='변경일자'),
    'business_id': fields.String(description='사업자번호'),
})

medicine_res_header = Medicines.model('주의사항 응답 header 정보', {
    'resultCode': fields.String(description='결과코드'),
    'resultMsg': fields.String(description='결과메시지')
})

medicine_warning_res = Medicines.model('단일 제품 주의사항 응답 모델', {
    'entpName': fields.String(description='업체명'),
    'itemName': fields.String(description='제품명'),
    'itemSeq': fields.String(description='품목기준코드'),
    'efcyQesitm': fields.String(description='문항1(효능)'),
    'useMethodQesitm': fields.String(description='문항2(사용법)'),
    'atpnWarnQesitm': fields.String(description='문항3(주의사항경고)'),
    'atpnQesitm': fields.String(description='문항4(주의사항)'),
    'intrcQesitm': fields.String(description='문항5(상호작용)'),
    'seQesitm': fields.String(description='문항6(부작용)'),
    'depositMethodQesitm': fields.String(description='문항7(보관법)'),
    'openDe': fields.String(description='공개일자'),
    'updateDe': fields.String(description='수정일자'),
    'itemImage': fields.String(description='낱알이미지'),
    'bizrno': fields.String(description='사업자등록번호')
})

medicine_score_res = Medicines.model('단일 제품 평점 응답 모델', {
    'score': fields.String(description='평점')
})

memos_fields = Medicines.model('memos 이하 모델', {
    'memo_id': fields.String(description='메모 ID'),
    'memo_img': fields.String(description='메모 내용')
})

memos_res_fields = Medicines.model('메모 목록 응답 모델', {
    'count': fields.Integer(description='메모들 총 개수'),
    'memos': fields.List(fields.Nested(memos_fields))
})

# medicine_res_body = Medicines.model('주의사항 응답 body 정보', {
#     'pageNo': fields.Integer(description='페이지번호'),
#     'totalCount': fields.Integer(description='전체 결과 수'),
#     'numOfRows': fields.Integer(description='한 페이지 결과 수'),
#     'items': fields.List(fields.Nested(medicine_res_items))
# })

# medicine_warning_res_fields = Medicines.model('단일 제품 주의사항 응답 모델', {
#     'header': fields.Nested(medicine_res_header),
#     'body': fields.Nested(medicine_res_body)
# })

# medicine_warning_res = Medicines.model('단일 제품 주의사항 응답 모델', {
#     'items': fields.List(fields.Nested(medicine_res_items))
# })

resource_parser = reqparse.RequestParser()
resource_parser.add_argument(
    "Authorization", help="Bearer {access_token}", type=str, required=True, location="headers", default="Bearer ")

request_score_parser = reqparse.RequestParser()
request_score_parser.add_argument(
    "Authorization", help="Bearer {access_token}", type=str, required=True, location="headers", default="Bearer ")
request_score_parser.add_argument(
    "score", type=str, required=True, location="body")

request_body_parser = reqparse.RequestParser()
request_body_parser.add_argument(
    "Authorization", help="Bearer {access_token}", type=str, required=True, location="headers", default="Bearer ")
request_body_parser.add_argument(
    "body", type=str, required=True, location="body")

status_message = Medicines.model(name="HTTP Status 메시지 모델", model={
    "msg": fields.String(description="Status 내용")
})


@Medicines.route('/<item_id>')
class Medicine(Resource):
    @Medicines.doc(description="""item_id에 해당하는 특정 제품의 상세 정보를 조회합니다.""")
    @Medicines.response(HTTPStatus.OK.value, '단일 제품 정보 조회 성공.', medicine_res_fields)
    @Medicines.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    def get(self, item_id):
        """단일 제품 정보 조회"""
        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)

        medicine = crudMedicine.get(item_id=item_id)
        medicine_dict = vars(medicine)
        del medicine_dict['_sa_instance_state']

        return medicine_dict, HTTPStatus.OK.value


@Medicines.route('/<item_id>/warning')
class MedicineWarning(Resource):
    @Medicines.doc(description="""item_id에 해당하는 특정 제품의 주의사항 정보를 조회합니다.""")
    @Medicines.response(HTTPStatus.OK.value, '주의사항 조회 성공.', medicine_warning_res)
    @Medicines.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @Medicines.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, '공공데이터 요청에 실패했습니다.', status_message)
    def get(self, item_id):
        """단일 제품 주의사항 조회"""
        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)

        url = api_url['warning']
        params = {
            'ServiceKey': Config.SERVICE_KEY,
            'itemSeq': item_id,
            'type': 'json'
        }

        response = requests.get(url=url, params=params)
        response_json = json.loads(response.text)

        if response_json["header"]["resultCode"] != '00':
            return make_response(jsonify(msg="Internal Server Error."), HTTPStatus.INTERNAL_SERVER_ERROR.value)

        return make_response(response_json["body"]["items"][0], HTTPStatus.OK.value)


@Medicines.route('/<item_id>/score')
class MedicineScore(Resource):
    @Medicines.doc(description="""item_id에 해당하는 특정 제품의 유저 평점을 조회합니다.""")
    @Medicines.expect(resource_parser)
    @Medicines.response(HTTPStatus.OK.value, '평점 조회 성공.', medicine_score_res)
    @Medicines.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @jwt_required
    def get(self, item_id):
        """단일 제품 평점 조회"""
        user_id = get_jwt_identity()

        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)

        return make_response(jsonify(score=crudRating.get_score(user_id=user_id, item_id=item_id)), HTTPStatus.OK.value)

    @Medicines.doc(description="""item_id에 해당하는 특정 제품의 유저 평점을 갱신합니다.""")
    @Medicines.expect(request_score_parser)
    @Medicines.response(HTTPStatus.OK.value, '평점 갱신 성공.', status_message)
    @Medicines.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @jwt_required
    def post(self, item_id):
        """단일 제품 평점 갱신"""
        args = Medicines.payload
        score = args.get('score')
        user_id = get_jwt_identity()

        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)

        crudRating.set(user_id=user_id, item_id=item_id, score=score)

        return make_response(jsonify(msg="Updated score."), HTTPStatus.OK.value)


@Medicines.route('/<item_id>/memo')
class MedicineMemo(Resource):
    @Medicines.doc(description="""item_id에 해당하는 제품에 대한 메모 목록을 조회합니다.""")
    @Medicines.expect(resource_parser)
    @Medicines.response(HTTPStatus.OK.value, '평점 조회 성공.', memos_res_fields)
    @Medicines.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @jwt_required
    def get(self, item_id):
        """메모 목록 조회"""
        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)

        memos = crudMemo.get_all(user_id=get_jwt_identity(), item_id=item_id)
        items = []
        data = {
            'count': len(memos),
            'memos': items
        }

        if memos is None or len(memos) == 0:
            data['count'] = 0
        else:
            for memo in memos:
                item = {
                    'memo_id': memo.id,
                    'memo_body': memo.body
                }
                items.append(item)

        return make_response(jsonify(data=data), HTTPStatus.OK.value)

    @Medicines.doc(description="""메모를 추가합니다.""")
    @Medicines.expect(request_body_parser)
    @Medicines.response(HTTPStatus.CREATED.value, '메모 추가 성공.', status_message)
    @Medicines.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @jwt_required
    def post(self, item_id):
        """메모 추가"""
        args = Medicines.payload
        body = args.get('body')
        user_id = get_jwt_identity()

        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)

        crudMemo.set(user_id=user_id, item_id=item_id, body=body)

        return make_response(jsonify(msg="Added memo."), HTTPStatus.CREATED.value)


@Medicines.route('/memo/<memo_id>')
class MedicineMemo(Resource):
    @Medicines.doc(description="""메모를 삭제합니다.""")
    @Medicines.expect(resource_parser)
    @Medicines.response(HTTPStatus.OK.value, '메모 삭제 성공.', status_message)
    @jwt_required
    def delete(self, memo_id):
        """메모 삭제"""
        crudMemo.delete(memo_id=memo_id)
        return make_response(jsonify(msg="Deleted memo."), HTTPStatus.OK.value)