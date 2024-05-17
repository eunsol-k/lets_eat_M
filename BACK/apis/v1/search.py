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
    'class_name_list': fields.List(fields.String(description='분류명 목록')),
    'entp_name': fields.String(description='업체명'),
    'item_image': fields.String(description='제품 이미지'),
    'etc_otc_name': fields.String(description='전문/일반')
})

search_res_fields = Search.model('통상 응답 모델', {
    'totalCount': fields.Integer(description='item 총 개수'),
    'items': fields.List(fields.Nested(search_fields))
})


@Search.route("/<search_value>")
class SearchGet(Resource):
    @Search.doc(description="""검색 결과 목록을 불러옵니다.\n제품명, 분류명으로 검색할 수 있습니다.""")
    @Search.response(HTTPStatus.OK.value, '검색 결과 조회 성공.', search_res_fields)
    def get(self, search_value):
        """검색 결과 목록 조회"""
        medicines = crudMedicine.get_by_search_value(search_value=search_value)
        
        items = []
        data = {
            'totalCount': len(medicines),
            'items': items
        }

        if medicines is None or len(medicines) == 0:
            data['totalCount'] = 0
        else:
            for medicine in medicines:
                class_name_list = []
                class_name = medicine.class_name
                etc_otc_name = medicine.etc_otc_name

                # 분류명 분별
                if class_name == '주로 그람양성, 음성균, 리케치아, 비루스에 작용하는 것':
                    class_name_list.extend(['그람 양성균', '그람 음성균', '리케치아', '비루스'])
                elif class_name == '해열.진통.소염제':
                    class_name_list.append('해열, 진통, 소염제')
                elif class_name == '주로 항산성균에 작용하는 것':
                    class_name_list.append('항산성균')
                elif class_name == '각성제,흥분제':
                    class_name_list.append('각성제, 흥분제')
                elif class_name == '주로 그람양성, 음성균에 작용하는 것':
                    class_name_list.extend(['그람 양성균', '그람 음성균'])
                elif class_name == '주로 그람양성균, 리케치아, 비루스에 작용하는 것':
                    class_name_list.extend(['그람 양성균', '리케치아', '비루스'])
                elif class_name == '주로 그람양성균에 작용하는 것':
                    class_name_list.append('그람 양성균')
                elif class_name == '주로 그람음성균에 작용하는 것':
                    class_name_list.append('그람 음성균')
                elif class_name == '주로 곰팡이, 원충에 작용하는 것':
                    class_name_list.append('곰팡이, 원충')
                elif class_name is not '':
                    class_name_list.append(class_name)

                # 일반/전문의약품 분별
                if etc_otc_name == '전문,희귀':
                    etc_otc_name = '전문, 희귀'
                elif etc_otc_name == '자격요법제(비특이성면역억제제를 포함)':
                    etc_otc_name = '자격요법제'
                elif etc_otc_name == '전문의약품':
                    etc_otc_name = '전문'
                elif etc_otc_name == '일반의약품':
                    etc_otc_name = '일반'

                item = {
                    'item_id': medicine.item_id,
                    'item_name': medicine.item_name,
                    'class_name_list': class_name_list,
                    'entp_name': medicine.entp_name,
                    'item_image': medicine.item_image,
                    'etc_otc_name': etc_otc_name
                }
                items.append(item)
        
        return make_response(data, HTTPStatus.OK.value)