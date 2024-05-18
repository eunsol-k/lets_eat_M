from flask import jsonify, make_response
from services.CRUDMedicine import CRUDMedicine
from services.CRUDRating import CRUDRating
from services.CRUDMemo import CRUDMemo
from http import HTTPStatus
from flask_restx import Resource, Namespace, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from configs.config import Config, api_url
from urllib.parse import unquote
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
    'entp_seq': fields.String(description='업소일련번호'),
    'entp_name': fields.String(description='업소명'),
    'chart': fields.String(description='성상'),
    'item_image': fields.String(description='큰제품이미지'),
    'disp_front': fields.String(description='표시앞'),
    'disp_back': fields.String(description='표시뒤'),
    'drug_shape': fields.String(description='의약품제형'),
    'color_front': fields.String(description='색상앞'),
    'color_back': fields.String(description='색상뒤'),
    'disv_front': fields.String(description='분할선앞'),
    'disv_back': fields.String(description='분할선뒤'),
    'size_long': fields.String(description='크기장축'),
    'size_short': fields.String(description='크기단축'),
    'size_thick': fields.String(description='크기두께'),
    'creat_date_img': fields.String(description='이미지생성일자(약학정보원)'),
    'class_id': fields.String(description='분류번호'),
    'class_name': fields.String(description='분류명'),
    'etc_otc_name': fields.String(description='전문일반구분'),
    'item_permit_date': fields.String(description='품목허가일자'),
    'form_code_name': fields.String(description='제형코드명'),
    'ind_front_cont': fields.String(description='표기내용앞'),
    'ind_back_cont': fields.String(description='표기내용뒤'),
    'ind_front_img': fields.String(description='표기이미지앞'),
    'ind_back_img': fields.String(description='표기이미지뒤'),
    'ind_front_code': fields.String(description='표기코드앞'),
    'ind_back_code': fields.String(description='표기코드뒤'),
    'modified_date': fields.String(description='변경일자'),
    'bizno': fields.String(description='사업자등록번호'),
    'bar_code': fields.String(description='표준코드'),
    'material_name': fields.List(fields.String(description='원료성분 목록')),
    'storage_method': fields.String(description='저장방법'),
    'valid_term': fields.String(description='유효기간'),
    'type_code': fields.String(description='유형코드'),
    'type_name': fields.String(description='DUR유형'),
    'edi_code': fields.String(description='보험코드'),
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

memos_fields = Medicines.model('메모 items 이하 모델', {
    'memo_id': fields.Integer(description='메모 ID'),
    'memo_body': fields.String(description='메모 내용'),
    'created_date': fields.String(description='메모 작성일')
})

memos_res_fields = Medicines.model('메모 목록 응답 모델', {
    'totalCount': fields.Integer(description='item 총 개수'),
    'items': fields.List(fields.Nested(memos_fields))
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
    "score", help="소숫점도 받을 수 있도록 String Type입니다.", type=str, required=True, location="body")

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
    @Medicines.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, '공공데이터 측에서 데이터를 보유하고 있지 않습니다.', status_message)
    def get(self, item_id):
        """단일 제품 정보 조회"""
        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)

        url = api_url['DUR']
        params = {
            'serviceKey': unquote(Config.SERVICE_KEY),
            'itemSeq': item_id,
            'type': 'json'
        }

        response = requests.get(url=url, params=params)
        response_json = json.loads(response.text)

        if response_json["header"]["resultCode"] != '00':
            return make_response(jsonify(msg="Internal Server Error."), HTTPStatus.INTERNAL_SERVER_ERROR.value)

        medicine = crudMedicine.get(item_id=item_id)
        medicine_dict = medicine.__dict__
        del medicine_dict['_sa_instance_state']

        if not response_json["body"]["totalCount"] == 0:
            dur_items = response_json["body"]["items"][0]
            
            material_name_list = []
            material_name_string = str(dur_items['MATERIAL_NAME'])
            material_name_arr = material_name_string.split('/')
            for material_name in material_name_arr:
                item = material_name.split(',')
                material_name_list.append(f'{item[0]}({item[4]}) {item[2]}{item[3]}')

            dur_dict = {
                'bar_code': dur_items['BAR_CODE'],  # 표준코드
                'material_name': material_name_list,  # 원료성분
                'storage_method': dur_items['STORAGE_METHOD'],  # 저장방법
                'valid_term': dur_items['VALID_TERM'],  # 유효기간
                'type_code': dur_items['TYPE_CODE'],  # 유형코드
                'type_name': dur_items['TYPE_NAME  '],  # DUR유형
                'edi_code': dur_items['EDI_CODE']  # 보험코드
            }

            medicine_dict.update(dur_dict)

        return medicine_dict, HTTPStatus.OK.value


@Medicines.route('/<item_id>/warning')
class MedicineWarning(Resource):
    @Medicines.doc(description="""item_id에 해당하는 특정 제품의 주의사항 정보를 조회합니다.""")
    @Medicines.response(HTTPStatus.OK.value, '주의사항 조회 성공.', medicine_warning_res)
    @Medicines.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @Medicines.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, '공공데이터 요청에 실패했습니다.', status_message)
    @Medicines.response(HTTPStatus.NO_CONTENT.value, '공공데이터 측에서 데이터를 보유하고 있지 않습니다.', status_message)
    def get(self, item_id):
        """단일 제품 주의사항 조회"""
        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)

        url = api_url['warning']
        params = {
            'ServiceKey': unquote(Config.SERVICE_KEY),
            'itemSeq': item_id,
            'type': 'json'
        }

        response = requests.get(url=url, params=params)
        response_json = json.loads(response.text)

        if response_json["header"]["resultCode"] != '00':
            return make_response(jsonify(msg="Internal Server Error."), HTTPStatus.INTERNAL_SERVER_ERROR.value)
        
        if response_json["body"]["totalCount"] == 0:
            return make_response(jsonify(msg="No Content."), HTTPStatus.NO_CONTENT.value)

        return make_response(response_json["body"]["items"][0], HTTPStatus.OK.value)


@Medicines.route('/<item_id>/score')
class MedicineScore(Resource):
    @Medicines.doc(description="""item_id에 해당하는 특정 제품의 유저 평점을 조회합니다.""")
    @Medicines.expect(resource_parser)
    @Medicines.response(HTTPStatus.OK.value, '평점 조회 성공.', medicine_score_res)
    @Medicines.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @Medicines.response(HTTPStatus.NO_CONTENT.value, '아직 평점이 없습니다.', status_message)
    @jwt_required()
    def get(self, item_id):
        """단일 제품 평점 조회"""
        user_id = get_jwt_identity()

        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)
        
        score = crudRating.get_score(user_id=user_id, item_id=item_id)
        if not score or score == "":
            return make_response(jsonify(msg="No Score value."), HTTPStatus.NO_CONTENT.value)

        return make_response(jsonify(score=crudRating.get_score(user_id=user_id, item_id=item_id)), HTTPStatus.OK.value)

    @Medicines.doc(description="""item_id에 해당하는 특정 제품의 유저 평점을 갱신합니다.""")
    @Medicines.expect(request_score_parser)
    @Medicines.response(HTTPStatus.OK.value, '평점 갱신 성공.', status_message)
    @Medicines.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @Medicines.response(HTTPStatus.BAD_REQUEST.value, '0 ~ 5 사이의 숫자를 문자열 형태로 입력해주세요.', status_message)
    @jwt_required()
    def post(self, item_id):
        """단일 제품 평점 갱신"""
        args = Medicines.payload
        score = args.get('score')
        user_id = get_jwt_identity()

        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)
        
        if score == None or score == "":
            return make_response(jsonify(msg="Request must be String Value between 0 and 5."), HTTPStatus.BAD_REQUEST.value)

        crudRating.set(user_id=user_id, item_id=item_id, score=score)

        return make_response(jsonify(msg="Updated score."), HTTPStatus.OK.value)


@Medicines.route('/<item_id>/memo')
class MedicineMemo(Resource):
    @Medicines.doc(description="""item_id에 해당하는 제품에 대한 메모 목록을 조회합니다.""")
    @Medicines.expect(resource_parser)
    @Medicines.response(HTTPStatus.OK.value, '메모 목록 조회 성공.', memos_res_fields)
    @Medicines.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @jwt_required()
    def get(self, item_id):
        """메모 목록 조회"""
        if not crudMedicine.is_exists(item_id=item_id):
            return make_response(jsonify(msg="Item Not Found."), HTTPStatus.NOT_FOUND.value)

        memos = crudMemo.get_all(user_id=get_jwt_identity(), item_id=item_id)
        items = []
        data = {
            'totalCount': len(memos),
            'items': items
        }

        if memos is None or len(memos) == 0:
            data['totalCount'] = 0
        else:
            for memo in memos:
                item = {
                    'memo_id': memo.id,
                    'memo_body': memo.body,
                    'created_date': memo.created_date
                }
                items.append(item)

        return make_response(data, HTTPStatus.OK.value)

    @Medicines.doc(description="""메모를 추가합니다.""")
    @Medicines.expect(request_body_parser)
    @Medicines.response(HTTPStatus.CREATED.value, '메모 추가 성공.', status_message)
    @Medicines.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 제품입니다.', status_message)
    @jwt_required()
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
    @Medicines.response(HTTPStatus.NO_CONTENT.value, '메모 삭제 성공.', status_message)
    @Medicines.response(HTTPStatus.NOT_FOUND.value, '존재하지 않는 메모 삭제 불가.', status_message)
    @jwt_required()
    def delete(self, memo_id):
        """메모 삭제"""
        memo = crudMemo.get(memo_id=memo_id)
        if not memo:
            return make_response(jsonify(msg="Cannot Found memo."), HTTPStatus.NOT_FOUND.value)

        crudMemo.delete(memo_id=memo_id)
        return make_response(jsonify(msg="Deleted memo."), HTTPStatus.NO_CONTENT.value)
