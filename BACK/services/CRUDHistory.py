from MODEL.session import Session
from MODEL.base_classes import History
from datetime import datetime


class CRUDHistory():
    def __init__(self) -> None:
        self.session = Session()

    def get(self, user_id, item_id) -> History:
        history = self.session.query(History).filter(
            History.user_id == user_id,
            History.item_id == item_id).scalar()
        return history

    def is_exists(self, user_id, item_id) -> bool:
        count = self.session.query(History).filter(
            History.user_id == user_id,
            History.item_id == item_id).count()
        if count > 0:
            return True
        else:
            return False

    def get_all_by_user(self, user_id, limit_num=10):
        histories = self.session.query(History).filter(
            History.user_id == user_id).order_by(History.modified_date.desc()).limit(limit_num).all()
        return histories

    def set(self, user_id, item_id):
        if self.is_exists(user_id=user_id, item_id=item_id):
            history = self.get(user_id=user_id, item_id=item_id)
            history.modified_date = datetime.today()
            self.session.commit()
        else:
            history = History(user_id=user_id, item_id=item_id, modified_date=datetime.today())
            self.session.add(history)
            self.session.commit()
