from MODEL.session import Session
from MODEL.base_classes import Medicine
from sqlalchemy import or_

class CRUDMedicine():
    def __init__(self) -> None:
        self.session = Session()
    
    def get(self, item_id) -> Medicine:
        medicine = self.session.query(Medicine).filter(
            Medicine.item_id == item_id).scalar()
        return medicine
    
    def is_exists(self, item_id) -> bool:
        count = self.session.query(Medicine).filter(
            Medicine.item_id == item_id).count()
        if count > 0:
            return True
        else:
            return False

    def get_by_search_value(self, search_value):
        medicines = self.session.query(Medicine).filter(or_(
            Medicine.item_name.like(f'%{search_value}%'),
            Medicine.class_name.like(f'%{search_value}%')
        )).all()
        if len(medicines) == 0:
            return []
        return medicines