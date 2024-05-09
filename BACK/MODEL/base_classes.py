from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, BigInteger
from MODEL.base import Base

class User(Base):
    __tablename__ = 'user'

    id = Column(String, primary_key=True)
    pw = Column(String)
    username = Column(String)
    expired_date = Column(DateTime)

    def __init__(self, id, pw, username):
        self.id = id
        self.pw = pw
        self.username = username

    def __repr__(self):
        return "<User('%s', '%s', '%s')>" % (self.id, self.pw, self.username)


class Search(Base):
    __tablename__ = 'search'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"))
    item_id = Column(Integer, ForeignKey("medicine.item_id", ondelete="CASCADE"))
    modified_date = Column(DateTime)

    def __init__(self, user_id, item_id, modified_date):
        self.user_id = user_id
        self.item_id = item_id
        self.modified_date = modified_date

    def __repr__(self):
        return "<Search('%s', '%d', '%s')>" % (self.user_id, self.item_id, self.modified_date)


class Rating(Base):
    __tablename__ = 'rating'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"))
    item_id = Column(Integer, ForeignKey(
        "medicine.item_id", ondelete="CASCADE"))
    score = Column(String)

    def __init__(self, user_id, item_id, score):
        self.user_id = user_id
        self.item_id = item_id
        self.score = score

    def __repr__(self):
        return "<Rating('%s', '%d', '%s')>" % (self.user_id, self.item_id, self.score)


class Interest(Base):
    __tablename__ = 'interest'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"))
    item_id = Column(Integer, ForeignKey(
        "medicine.item_id", ondelete="CASCADE"))
    updated_date = Column(DateTime)

    def __init__(self, user_id, item_id, updated_date):
        self.user_id = user_id
        self.item_id = item_id
        self.updated_date = updated_date

    def __repr__(self):
        return "<Interest('%s', '%d', '%s')>" % (self.user_id, self.item_id, self.updated_date)


class Notice(Base):
    __tablename__ = 'notice'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    body = Column(Text)
    created_date = Column(DateTime)
    modified_date = Column(DateTime)

    def __init__(self, title, body, created_date, modified_date):
        self.title = title
        self.body = body
        self.created_date = created_date
        self.modified_date = modified_date

    def __repr__(self):
        return "<Notice('%s', '%s', '%s', '%s')>" % (self.title, self.body, self.created_date, self.modified_date)


class Memo(Base):
    __tablename__ = 'memo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey(
        "medicine.item_id", ondelete="CASCADE"))
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"))
    body = Column(Text)
    created_date = Column(DateTime)
    modified_date = Column(DateTime)

    def __init__(self, item_id, user_id, body, created_date, modified_date):
        self.item_id = item_id
        self.user_id = user_id
        self.body = body
        self.created_date = created_date
        self.modified_date = modified_date

    def __repr__(self):
        return "<Memo('%d', '%s', '%s', '%s', '%s')>" % (self.item_id, self.user_id, self.body, self.created_date, self.modified_date)


class Medicine(Base):
    __tablename__ = 'medicine'

    item_id = Column(Integer, primary_key=True)
    item_name = Column(String)
    enter_id = Column(Integer)
    enter_name = Column(String)
    constell = Column(String)
    product_img = Column(String)
    disp_front = Column(String)
    disp_back = Column(String)
    item_formul = Column(String)
    color_front = Column(String)
    color_back = Column(String)
    disv_front = Column(String)
    disv_back = Column(String)
    size_long = Column(String)
    size_short = Column(String)
    size_thick = Column(String)
    creat_date_img = Column(String)
    class_id = Column(Integer)
    calss_name = Column(String)
    sp_ge = Column(String)
    app_date_item = Column(String)
    formul_name = Column(String)
    ind_front_cont = Column(String)
    ind_back_cont = Column(String)
    ind_front_img = Column(String)
    ind_back_img = Column(String)
    ind_front_code = Column(String)
    ind_back_code = Column(String)
    modified_date = Column(String)
    business_id = Column(BigInteger)

    def __init__(self, item_id, item_name, enter_id, enter_name, constell, product_img, disp_front, disp_back, item_formul, color_front, color_back, disv_front, disv_back, size_long, size_short, size_thick, creat_date_img, class_id, calss_name, sp_ge, app_date_item, formul_name, ind_front_cont, ind_back_cont, ind_front_img, ind_back_img, ind_front_code, ind_back_code, modified_date, business_id):
        self.item_id = item_id
        self.item_name = item_name
        self.enter_id = enter_id
        self.enter_name = enter_name
        self.constell = constell
        self.product_img = product_img
        self.disp_front = disp_front
        self.disp_back = disp_back
        self.item_formul = item_formul
        self.color_front = color_front
        self.color_back = color_back
        self.disv_front = disv_front
        self.disv_back = disv_back
        self.size_long = size_long
        self.size_short = size_short
        self.size_thick = size_thick
        self.creat_date_img = creat_date_img
        self.class_id = class_id
        self.calss_name = calss_name
        self.sp_ge = sp_ge
        self.app_date_item = app_date_item
        self.formul_name = formul_name
        self.ind_front_cont = ind_front_cont
        self.ind_back_cont = ind_back_cont
        self.ind_front_img = ind_front_img
        self.ind_back_img = ind_back_img
        self.ind_front_code = ind_front_code
        self.ind_back_code = ind_back_code
        self.modified_date = modified_date
        self.business_id = business_id

    def __repr__(self):
        return "<Medicine('%d', '%s')>" % (self.item_id, self.item_name)
