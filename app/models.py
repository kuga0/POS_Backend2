from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# 商品マスタモデル
class Product(Base):
    __tablename__ = "products"

    PRD_ID = Column(Integer, primary_key=True, index=True)
    PRD_CODE = Column(String(13), unique=True, index=True)  # 商品コードはユニーク
    FROM_DATE = Column(DateTime)
    TO_DATE = Column(DateTime)
    NAME = Column(String(50))
    PRICE = Column(Integer)

    promotions = relationship("Promotion", back_populates="product")

# 販促企画モデル
class Promotion(Base):
    __tablename__ = "promotions"

    PRM_ID = Column(Integer, primary_key=True, index=True)
    PRM_CODE = Column(String(13), unique=True, index=True)
    FROM_DATE = Column(DateTime)
    TO_DATE = Column(DateTime)
    NAME = Column(String(50))
    PERCENT = Column(Float)
    DISCOUNT = Column(Integer)
    PRD_ID = Column(Integer, ForeignKey('products.PRD_ID'))

    product = relationship("Product", back_populates="promotions")

# 取引モデル
class Transaction(Base):
    __tablename__ = "transactions"

    TRD_ID = Column(Integer, primary_key=True, index=True)
    DATETIME = Column(DateTime, default=datetime.now)
    EMP_CD = Column(String(10), default="9999999999")
    STORE_CD = Column(String(5), default="30")
    POS_NO = Column(String(3), default="90")
    TOTAL_AMT = Column(Integer, default=0)
    TTL_AMT_EX_TAX = Column(Integer, default=0)

    details = relationship("TransactionDetail", back_populates="transaction")

# 取引明細モデル
class TransactionDetail(Base):
    __tablename__ = "transaction_details"

    TRD_ID = Column(Integer, ForeignKey('transactions.TRD_ID'), primary_key=True)
    DTL_ID = Column(Integer, primary_key=True, index=True)  # 取引明細一意キー
    PRD_ID = Column(Integer, ForeignKey('products.PRD_ID'))
    PRD_CODE = Column(String(13))
    PRD_NAME = Column(String(50))
    PRD_PRICE = Column(Integer)
    TAX_CD = Column(String(2), default="10")  # 消費税区分

    transaction = relationship("Transaction", back_populates="details")

# 税マスタモデル
class TaxMaster(Base):
    __tablename__ = "tax_master"

    ID = Column(Integer, primary_key=True, index=True)
    CODE = Column(String(2), unique=True)  # ユニーク制約
    NAME = Column(String(20))
    PERCENT = Column(Float)

# テーブル作成用の関数
def create_tables(engine):
    Base.metadata.create_all(bind=engine)
