from flask import make_response
from services.CRUDMedicine import CRUDMedicine
from services.CRUDMemo import CRUDMemo
from services.CRUDInterest import CRUDInterest
from http import HTTPStatus
from flask_restx import Resource, Namespace, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity


crudMedicine = CRUDMedicine()
crudMemo = CRUDMemo()
crudInterest = CRUDInterest()


Users = Namespace(
    name='Users',
    description='유저 관리 기능 관련 API'
)


by_medicine_item_fields = Users.model('제품별 item 모델', {
    'memo_num_per_item': fields.Integer(description='해당 제품의 메모 개수'),
    'item_id': fields.Integer(description='제품 ID'),
    'item_name': fields.Integer(description='제품명'),
    'item_image': fields.Integer(description='제품 이미지'),
    'is_liked': fields.Integer(description='제품 좋아요 표시 여부'),
    'last_updated_date': fields.DateTime(description='제품의 마지막 메모 일자'),
})

by_desc_item_fields = Users.model('내림차순 item 모델', {
    'memo_id': fields.Integer(description='메모 ID'),
    'memo_body': fields.Integer(description='메모 내용'),
    'created_date': fields.Integer(description='메모 생성일'),
    'item_id': fields.Integer(description='제품 ID'),
    'item_name': fields.Integer(description='제품명')
})

by_medicine_fields = Users.model('제품별 메모 목록', {
    'totalCount': fields.Integer(description='메모된 제품 총 개수'),
    'items': fields.List(fields.Nested(by_medicine_item_fields))
})

by_desc_fields = Users.model('내림차순 메모 목록', {
    'totalCount': fields.Integer(description='메모들 총 개수'),
    'items': fields.List(fields.Nested(by_desc_item_fields))
})

memo_list_res_fields = Users.model('메모 목록 응답 모델', {
    'by_medicine': fields.Nested(by_medicine_fields),
    'by_desc': fields.Nested(by_desc_fields)
})

resource_parser = reqparse.RequestParser()
resource_parser.add_argument(
    "Authorization", help="Bearer {access_token}", type=str, required=True, location="headers", default="Bearer ")


@Users.route("/memo")
class UserMemo(Resource):
    @Users.doc(description="""유저의 메모 목록을 조회합니다.\n제품별 또는 내림차순으로 확인할 수 있습니다.""")
    @Users.expect(resource_parser)
    @Users.response(HTTPStatus.OK.value, '메모 목록 조회 성공.', memo_list_res_fields)
    @jwt_required()
    def get(self):
        """유저 메모 목록 조회"""
        user_id = get_jwt_identity()

        # 내림차순 조회
        memo_desc_list = crudMemo.get_all_by_user(user_id=user_id)
        items_desc = []
        by_desc = {
            'totalCount': 0,
            'items': items_desc
        }

        if memo_desc_list is not None and len(memo_desc_list) > 0:
            for memo_desc in memo_desc_list:
                medicine = crudMedicine.get(item_id=memo_desc.item_id)

                item = {
                    'memo_id': memo_desc.id,
                    'memo_body': memo_desc.body,
                    'created_date': memo_desc.created_date,
                    'item_id': memo_desc.item_id,
                    'item_name': medicine.item_name
                }

                items_desc.append(item)
            by_desc['totalCount'] = len(memo_desc_list)

        # 제품별 조회
        medicine_id_list = crudMedicine.get_all_by_user_written(user_id=user_id)
        items_medicine = []
        by_medicine = {
            'totalCount': 0,
            'items': items_medicine
        }

        if medicine_id_list is not None and len(medicine_id_list) > 0:
            for medicine_id in medicine_id_list:
                medicine_id_str = str(medicine_id)
                medicine_id_splitted = medicine_id_str.split("'")

                memos = crudMemo.get_all(
                    user_id=user_id, item_id=medicine_id_splitted[1])
                is_liked = crudInterest.is_exists(
                    user_id=user_id, item_id=medicine_id_splitted[1])
                medicine = crudMedicine.get(item_id=medicine_id_splitted[1])


                item = {
                    'memo_num_per_item': len(memos),
                    'item_id': medicine.item_id,
                    'item_name': medicine.item_name,
                    'item_image': medicine.item_image,
                    'is_liked': is_liked,
                    'last_updated_date': memos[0].created_date
                }

                items_medicine.append(item)
            by_medicine['totalCount'] = len(medicine_id_list)

        data = {
            'by_medicine': by_medicine,
            'by_desc': by_desc
        }

        print(f'data: {data}')


        return make_response(data, HTTPStatus.OK.value)
