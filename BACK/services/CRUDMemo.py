from MODEL.session import Session
from MODEL.base_classes import Memo
from datetime import datetime

class CRUDMemo():
    def __init__(self) -> None:
        self.session = Session()
    
    def get_all(self, user_id, item_id):
        memos = self.session.query(Memo).filter(
            Memo.user_id == user_id,
            Memo.item_id == item_id).order_by(Memo.modified_date.desc()).all()
        return memos

    def get(self, memo_id):
        memo = self.session.query(Memo).filter(
            Memo.id == memo_id).scalar()
        return memo

    # 현재는 메모 수정 기능이 없음, 작성일과 수정일을 무조건 같게
    def set(self, user_id, item_id, body):
        memo = Memo(user_id=user_id, item_id=item_id,
                    body=body, created_date=datetime.today(), modified_date=datetime.today())
        self.session.add(memo)
        self.session.commit()
    
    def delete(self, memo_id):
        memo = self.session.query(Memo).filter(Memo.id == memo_id).scalar()
        self.session.delete(memo)
        self.session.commit()
