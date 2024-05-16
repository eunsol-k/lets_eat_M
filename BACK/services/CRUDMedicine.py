from MODEL.session import Session
from MODEL.base_classes import Medicine

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
    
    def get_by_item_name(self, item_name):
        medicines = self.session.query(Medicine).filter(
            Medicine.item_name.like(f'%{item_name}%')
        ).all()
        if len(medicines) == 0:
            return []
        return medicines