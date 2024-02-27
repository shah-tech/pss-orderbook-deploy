from sqlalchemy.types import *
from sqlalchemy.sql import func

from sqlalchemy import Column, ForeignKey, create_engine, Table, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


Users_Roles_Bridge = Table(
    "UserRoles",
    Base.metadata,
    Column("roleid", ForeignKey("Role.roleid", name="fk_roleid_userRoleBridge"), primary_key=True),
    Column("userid", ForeignKey("User.userid", name="fk_userid_userRoleBridge"), primary_key=True)
)


class User(Base):
    __tablename__ = 'User'

    userid = Column(Integer, primary_key=True)
    uname = Column(String(45), unique=True)
    password = Column(String(45))
    role = relationship('Role', secondary=Users_Roles_Bridge, back_populates='user')
    product = relationship('Order', back_populates='user')
    dateJoined = Column(DateTime, server_default =func.now() )

class Role(Base):
    __tablename__ = 'Role'
    roleid = Column(Integer, primary_key=True)
    name = Column(String(24), unique=True)
    user = relationship('User', secondary=Users_Roles_Bridge, back_populates="role")

class Product(Base):
    __tablename__="Product"

    symbol = Column(String(16), primary_key=True)
    price = Column(DECIMAL(15,2))
    productType = Column(String(12))
    name = Column(String(128))
    lastUpdate= Column(DateTime)
    user = relationship('Order',  back_populates="product")

class Order(Base):
    __tablename__='Order'

    orderid = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('User.userid'))
    symbol = Column(String(16), ForeignKey('Product.symbol'))
    side = Column(Integer)
    orderTime = Column(DateTime, server_default =func.now() )
    shares = Column(Integer)
    price = Column(DECIMAL(15,2))
    status = Column(String(24), server_default="pending") # filled, partial_fill, or cancled
    user = relationship("User", back_populates="product")
    product = relationship("Product", back_populates="user")
    fill = relationship("Fill", back_populates="order")

class Fill(Base):
    __tablename__="Fill"
    fillid = Column(Integer, primary_key=True)
    orderid = Column(Integer, ForeignKey('Order.orderid'))
    userid = Column(Integer, ForeignKey('User.userid'))
    share = Column(Integer)
    order = relationship("Order", back_populates="fill")
    price = Column(DECIMAL(15,2))
    symbol = Column(String(16), ForeignKey('Product.symbol'))

