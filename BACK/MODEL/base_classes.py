from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, Boolean
from MODEL.base import Base
import json

class User(Base):
    __tablename__ = 'user'

    id = Column(String, primary_key=True)
    pw = Column(String)
    username = Column(String)
    role = Column(String)
    expired_date = Column(DateTime)

    def __init__(self, id, pw, username, role='User', expired_date=None):
        self.id = id
        self.pw = pw
        self.username = username
        self.role = role
        self.expired_date = expired_date

    def __repr__(self):
        return "<User('%s', '%s', '%s', %s)>" % (self.id, self.pw, self.username, self.role)


class History(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"))
    item_id = Column(String, ForeignKey(
        "medicine.item_id", ondelete="CASCADE"))
    modified_date = Column(DateTime)

    def __init__(self, user_id, item_id, modified_date):
        self.user_id = user_id
        self.item_id = item_id
        self.modified_date = modified_date

    def __repr__(self):
        return "<History('%s', '%s', '%s')>" % (self.user_id, self.item_id, self.modified_date)


class Rating(Base):
    __tablename__ = 'rating'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"))
    item_id = Column(String, ForeignKey(
        "medicine.item_id", ondelete="CASCADE"))
    score = Column(String)

    def __init__(self, user_id, item_id, score):
        self.user_id = user_id
        self.item_id = item_id
        self.score = score

    def __repr__(self):
        return "<Rating('%s', '%s', '%s')>" % (self.user_id, self.item_id, self.score)


class Interest(Base):
    __tablename__ = 'interest'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"))
    item_id = Column(String, ForeignKey(
        "medicine.item_id", ondelete="CASCADE"))
    modified_date = Column(DateTime)

    def __init__(self, user_id, item_id, modified_date):
        self.user_id = user_id
        self.item_id = item_id
        self.modified_date = modified_date

    def __repr__(self):
        return "<Interest('%s', '%s', '%s)>" % (self.user_id, self.item_id, self.modified_date)


class Notice(Base):
    __tablename__ = 'notice'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    body = Column(Text)
    created_date = Column(DateTime)
    modified_date = Column(DateTime)
    hits = Column(Integer, default=0)
    fixed = Column(Boolean, default=False)

    def __init__(self, title, body, created_date, modified_date, hits, fixed):
        self.title = title
        self.body = body
        self.created_date = created_date
        self.modified_date = modified_date
        self.hits = hits
        self.fixed = fixed

    def __repr__(self):
        return "<Notice('%s', '%s', '%s', '%s', '%d', '%s')>" % (self.title, self.body, self.created_date, self.modified_date, self.hits, self.fixed)


class Memo(Base):
    __tablename__ = 'memo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"))
    item_id = Column(String, ForeignKey(
        "medicine.item_id", ondelete="CASCADE"))
    body = Column(Text)
    created_date = Column(DateTime)
    modified_date = Column(DateTime)

    def __init__(self, user_id, item_id, body, created_date, modified_date):
        self.user_id = user_id
        self.item_id = item_id
        self.body = body
        self.created_date = created_date
        self.modified_date = modified_date

    def __repr__(self):
        return "<Memo('%s', '%s', '%s', '%s', '%s')>" % (self.user_id, self.item_id, self.body, self.created_date, self.modified_date)


class Medicine(Base):
    __tablename__ = 'medicine'

    item_id = Column(String, primary_key=True)
    item_name = Column(String)
    entp_seq = Column(String)
    entp_name = Column(String)
    chart = Column(String)
    item_image = Column(String)
    disp_front = Column(String)
    disp_back = Column(String)
    drug_shape = Column(String)
    color_front = Column(String)
    color_back = Column(String)
    disv_front = Column(String)
    disv_back = Column(String)
    size_long = Column(String)
    size_short = Column(String)
    size_thick = Column(String)
    creat_date_img = Column(String)
    class_id = Column(String)
    class_name = Column(String)
    etc_otc_name = Column(String)
    item_permit_date = Column(String)
    form_code_name = Column(String)
    ind_front_cont = Column(String)
    ind_back_cont = Column(String)
    ind_front_img = Column(String)
    ind_back_img = Column(String)
    ind_front_code = Column(String)
    ind_back_code = Column(String)
    modified_date = Column(String)
    bizno = Column(String)

    def __init__(self, item_id, item_name, entp_seq, entp_name, chart, item_image, disp_front, disp_back, drug_shape, color_front, color_back, disv_front, disv_back, size_long, size_short, size_thick, creat_date_img, class_id, class_name, etc_otc_name, item_permit_date, form_code_name, ind_front_cont, ind_back_cont, ind_front_img, ind_back_img, ind_front_code, ind_back_code, modified_date, bizno):
        self.item_id = item_id
        self.item_name = item_name
        self.entp_seq = entp_seq
        self.entp_name = entp_name
        self.chart = chart
        self.item_image = item_image
        self.disp_front = disp_front
        self.disp_back = disp_back
        self.drug_shape = drug_shape
        self.color_front = color_front
        self.color_back = color_back
        self.disv_front = disv_front
        self.disv_back = disv_back
        self.size_long = size_long
        self.size_short = size_short
        self.size_thick = size_thick
        self.creat_date_img = creat_date_img
        self.class_id = class_id
        self.class_name = class_name
        self.etc_otc_name = etc_otc_name
        self.item_permit_date = item_permit_date
        self.form_code_name = form_code_name
        self.ind_front_cont = ind_front_cont
        self.ind_back_cont = ind_back_cont
        self.ind_front_img = ind_front_img
        self.ind_back_img = ind_back_img
        self.ind_front_code = ind_front_code
        self.ind_back_code = ind_back_code
        self.modified_date = modified_date
        self.bizno = bizno

    def __repr__(self):
        return "<Medicine('%s', '%s')>" % (self.item_id, self.item_name)