from flask import jsonify, make_response
from services.CRUDMedicine import CRUDMedicine
from http import HTTPStatus
from flask_restx import Resource, Namespace, fields


crudMedicine = CRUDMedicine()


Search = Namespace(
    name='Search',
    description='제품 검색 기능 관련 API'
)


search_fields = Search.model('검색 items 이하 모델', {
    'item_id': fields.String(description='제품 ID'),
    'item_name': fields.String(description='제품명'),
    'class_name': fields.String(description='분류명'),
    'entp_name': fields.String(description='업체명'),
    'item_image': fields.String(description='제품 이미지'),
    'etc_otc_name': fields.String(description='전문/일반')
})

search_res_fields = Search.model('통상 응답 모델', {
    'totalCount': fields.Integer(description='item 총 개수'),
    'items': fields.List(fields.Nested(search_fields))
})


@Search.route("/<item_name>")
class SearchGet(Resource):
    @Search.doc(description="""검색 결과 목록을 불러옵니다.""")
    @Search.response(HTTPStatus.OK.value, '검색 결과 조회 성공.', search_res_fields)
    def get(self, item_name):
        """검색 결과 목록 조회"""
        medicines = crudMedicine.get_by_item_name(item_name=item_name)

        items = []
        data = {
            'totalCount': len(medicines),
            'items': items
        }

        if medicines is None or len(medicines) == 0:
            data['totalCount'] = 0
        else:
            for medicine in medicines:
                item = {
                    'item_id': medicine.item_id,
                    'item_name': medicine.item_name,
                    'class_name': medicine.class_name,
                    'entp_name': medicine.entp_name,
                    'item_image': medicine.item_image,
                    'etc_otc_name': medicine.etc_otc_name
                }
                items.append(item)
        
        return make_response(data, HTTPStatus.OK.value)
