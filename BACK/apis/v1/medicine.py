from flask import jsonify, make_response
from MODEL.base_classes import User
from services.CRUDUser import CRUDUser
from services.CRUDInterest import CRUDInterest
from services.CRUDMedicine import CRUDMedicine
from http import HTTPStatus
from flask_restx import Resource, Namespace, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from configs.config import Config, api_url
import json
import requests


crudUser = CRUDUser()
crudInterest = CRUDInterest()
crudMedicine = CRUDMedicine()


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

medicine_warning_res = medicine_res_body = Medicines.model('단일 제품 주의사항 응답 모델', {
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

request_parser = reqparse.RequestParser()
request_parser.add_argument(
    "Authorization", help="Bearer {access_token}", type=str, required=True, location="headers", default="Bearer ")
request_parser.add_argument(
    "item_id", type=str, required=True, location="body")

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


@Medicines.route('/warning/<item_id>')
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
