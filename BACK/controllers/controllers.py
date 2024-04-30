from flask import Blueprint, jsonify
import services.services as ex_service
from services.CRUDBase import CRUDMedicine

ex_bp = Blueprint(name='example', import_name=__name__, url_prefix='/example')

@ex_bp.route('/', methods=['GET'])
def ex_route() -> str:
    data = 196000003

    crudMedicine = CRUDMedicine()

    result = crudMedicine.get(id=data)
    print(result)
    return jsonify(result=result.item_name)

@ex_bp.route('/<int:user_number>', methods=['GET'])
def ex_route_add_param(user_number: int) -> str:
    result = ex_service.ex_route_add_param(user_number)
    return jsonify(result=result)