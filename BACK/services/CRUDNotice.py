from MODEL.session import Session
from MODEL.base_classes import Notice
from datetime import datetime


class CRUDNotice():
    def __init__(self) -> None:
        self.session = Session()

    def get_all(self):
        notices_fixed = self.session.query(Notice).filter(
            Notice.fixed == True).order_by(
            Notice.created_date.desc()).all()
        
        notices_unfixed = self.session.query(Notice).filter(
            Notice.fixed == False).order_by(
            Notice.created_date.desc()).all()
        
        notices_fixed.extend(notices_unfixed)
        if len(notices_fixed) == 0:
            return []
        
        return notices_fixed

    def get(self, notice_id) -> Notice:
        notice = self.session.query(Notice).filter(
            Notice.id == notice_id).scalar()
        return notice

    def set(self, title, body, fixed=False):
        notice = Notice(title=title, body=body, created_date=datetime.today(), modified_date=None, hits=0, fixed=fixed)
        self.session.add(notice)
        self.session.commit()
    
    def update(self, notice_id, title=None, body=None, fixed=None):
        notice = self.get(notice_id=notice_id)
        if title is not None:
            notice.title = title
        if body is not None:
            notice.body = body
        if fixed is not None:
            notice.fixed = fixed

        notice.modified_date = datetime.today()
        self.session.commit()
    
    def delete(self, notice_id):
        notice = self.get(notice_id=notice_id)
        self.session.delete(notice)
        self.session.commit()
    
    def update_hits(self, notice_id):
        self.session.query(Notice).filter(
            Notice.id == notice_id).update({'hits': Notice.hits + 1})
        self.session.commit()
    
    def change_fixed_value(self, notice_id):
        notice = self.get(notice_id=notice_id)
        notice.fixed = not notice.fixed
        self.session.commit()
