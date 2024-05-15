from MODEL.session import Session
from MODEL.base_classes import Rating

class CRUDRating():
    def __init__(self) -> None:
        self.session = Session()
    
    def get(self, user_id, item_id) -> Rating:
        rating = self.session.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.item_id == item_id).scalar()
        return rating

    def is_exists(self, user_id, item_id) -> bool:
        count = self.session.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.item_id == item_id).count()
        if count > 0:
            return True
        else:
            return False

    def get_score(self, user_id, item_id):
        if self.is_exists(user_id=user_id, item_id=item_id):
            rating = self.get(user_id=user_id, item_id=item_id)
            return rating.score
        else:
            return None

    def set(self, user_id, item_id, score):
        if self.is_exists(user_id=user_id, item_id=item_id):
            rating = self.get(user_id=user_id, item_id=item_id)
            rating.score = score
            self.session.commit()
        else:
            rating = Rating(user_id=user_id, item_id=item_id, score=score)
            self.session.add(rating)
            self.session.commit()
