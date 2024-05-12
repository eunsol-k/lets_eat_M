from MODEL.session import Session
from datetime import datetime
from MODEL.base_classes import User
import bcrypt


class CRUDUser():
    def __init__(self) -> None:
        self.session = Session()

    def set(self, user: User) -> bool:
        if not self.is_exists_by_id(user_id=user.id):
            self.session.add(user)
            self.session.commit()
            return True
        # elif self.is_expired(user_id=user.id):
        #     self.delete(user_id=user.id)
        #     self.session.add(user)
        #     self.session.commit()
        #     return True
        else:
            return False
    
    def get(self, user_id) -> User:
        user = self.session.query(User).filter(
            User.id == user_id).scalar()
        return user
    
    def is_exists_by_id(self, user_id) -> bool:
        count = self.session.query(User).filter(
            User.id == user_id).count()
        if count > 0:
            return True
        else:
            return False
    
    def is_expired(self, user_id) -> bool:
        user = self.get(user_id=user_id)
        if user.expired_date is not None:
            return True
        else:
            return False
    
    def is_correct(self, user_id, user_pw:str) -> bool:
        user = self.get(user_id=user_id)
        hashed_pw = user.pw
        if bcrypt.checkpw(user_pw.encode("utf-8"), hashed_pw.encode("utf-8")):
            return True
        else:
            return False

    def update_username(self, user_id, username):
        self.session.query(User).filter(User.id == user_id).update({'username': username})
        self.session.commit()
    
    def update_pw(self, user_id, user_pw):
        self.session.query(User).filter(
            User.id == user_id).update({'pw': user_pw})
        self.session.commit()

    def update_expired_date(self, user_id):
        self.session.query(User).filter(
            User.id == user_id).update({'expired_date': datetime.today()})
        self.session.commit()

    def delete(self, user_id):
        user = self.session.query(User).filter(User.id == user_id).scalar()
        self.session.delete(user)
        self.session.commit()