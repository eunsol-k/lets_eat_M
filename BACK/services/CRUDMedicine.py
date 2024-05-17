from MODEL.session import Session
from MODEL.base_classes import Medicine, Memo
from sqlalchemy import or_, distinct

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
    
    def get_all_by_user_written(self, user_id):
        medicines = self.session.query(distinct(Medicine.item_id)).join(
            Memo, Medicine.item_id == Memo.item_id).filter(
                Memo.user_id == user_id
        ).all()
        return medicines