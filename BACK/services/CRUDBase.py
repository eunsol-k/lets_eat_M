from MODEL.session import Session
from MODEL.base_classes import Medicine 

class CRUDMedicine():
    def __init__(self) -> None:
        self.session = Session()

    def get(self, id: int) -> Medicine:
        medicine = self.session.query(Medicine).filter(
            Medicine.item_id == id).first()
        return medicine