from MODEL.session import Session
from MODEL.base_classes import Interest
from datetime import datetime

class CRUDInterest():
    def __init__(self) -> None:
        self.session = Session()
    
    def on(self, user_id, item_id):
        interest = Interest(user_id=user_id, item_id=item_id, modified_date=datetime.today())
        self.session.add(interest)
        self.session.commit()

    def off(self, user_id, item_id):
        interest = self.get(user_id=user_id, item_id=item_id)
        self.session.delete(interest)
        self.session.commit()

    def get(self, user_id, item_id) -> Interest:
        interest = self.session.query(Interest).filter(
            Interest.user_id == user_id,
            Interest.item_id == item_id).scalar()
        return interest
        
    def is_exists(self, user_id, item_id) -> bool:
        count = self.session.query(Interest).filter(
            Interest.user_id == user_id,
            Interest.item_id == item_id).count()
        if count > 0:
            return True
        else:
            return False

    def get_all_by_user(self, user_id):
        likes = self.session.query(Interest).filter(
            Interest.user_id == user_id).order_by(Interest.modified_date.desc()).all()
        if len(likes) == 0:
            return []
        return likes