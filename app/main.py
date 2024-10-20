from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# DBの設定
DATABASE_URL = "sqlite:///./test.db"  # 開発用にはSQLiteを使用。実運用ではMySQLなどに切り替える
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 仮の商品マスタデータ
product_master = {
    "12345678901": {"name": "おーいお茶", "price": 150},
    "98765432101": {"name": "ソフラン", "price": 300},
}

# データベースモデル
class ProductMaster(Base):
    __tablename__ = "product_master"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    price = Column(Integer)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime, default=datetime.utcnow)
    emp_code = Column(String(10), default="9999999999")
    store_code = Column(String(5), default="30")
    pos_no = Column(String(3), default="90")
    total_amt = Column(Integer, default=0)
    ttl_amt_ex_tax = Column(Integer, default=0)

class TransactionDetail(Base):
    __tablename__ = "transaction_details"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    product_id = Column(Integer)
    product_code = Column(String)
    product_name = Column(String)
    product_price = Column(Integer)
    tax_code = Column(String, default="10")

class TaxMaster(Base):
    __tablename__ = "tax_master"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)
    percent = Column(Integer)

Base.metadata.create_all(bind=engine)

# モデル定義
class ProductRequest(BaseModel):
    code: str

class ProductResponse(BaseModel):
    code: str
    name: str
    price: int

class PurchaseItem(BaseModel):
    code: str
    name: str
    price: int

class PurchaseRequest(BaseModel):
    emp_code: str
    store_code: str
    pos_id: str
    items: List[PurchaseItem]

class PurchaseResponse(BaseModel):
    success: bool
    total_amount: int
    total_amount_ex_tax: int

# トップページ用のテキストを取得するエンドポイント
@app.get("/greeting")
def get_greeting():
    return {"message": "こんにちは！"}

# 商品検索API（仮データベースを使用）
@app.post("/product_search", response_model=ProductResponse)
def product_search(request: ProductRequest):
    # まず仮の商品マスタデータを確認
    product = product_master.get(request.code)
    if product:
        return {"code": request.code, "name": product["name"], "price": product["price"]}

    # 仮データになければDBから検索
    session = SessionLocal()
    db_product = session.query(ProductMaster).filter(ProductMaster.code == request.code).first()
    session.close()
    if db_product:
        return {"code": db_product.code, "name": db_product.name, "price": db_product.price}
    else:
        raise HTTPException(status_code=404, detail="商品がマスタ未登録です")

# 購入API
@app.post("/purchase", response_model=PurchaseResponse)
def purchase(request: PurchaseRequest):
    session = SessionLocal()
    # 取引レコードを作成
    transaction = Transaction(
        emp_code=request.emp_code or "9999999999",
        store_code=request.store_code,
        pos_no=request.pos_id
    )
    session.add(transaction)
    session.commit()

    # 合計金額の計算
    total_amount = 0
    total_amount_ex_tax = 0
    tax_rate = session.query(TaxMaster).filter(TaxMaster.code == "10").first().percent

    for item in request.items:
        total_amount_ex_tax += item.price
        total_amount += item.price * (1 + tax_rate)

        # 取引明細レコードを作成
        transaction_detail = TransactionDetail(
            transaction_id=transaction.id,
            product_id=item.code,
            product_code=item.code,
            product_name=item.name,
            product_price=item.price,
            tax_code="10"
        )
        session.add(transaction_detail)
    
    # 取引の合計金額を更新
    transaction.total_amt = total_amount
    transaction.ttl_amt_ex_tax = total_amount_ex_tax
    session.commit()
    session.close()

    return {
        "success": True,
        "total_amount": total_amount,
        "total_amount_ex_tax": total_amount_ex_tax
    }

# 全商品取得API（デバッグ用）
@app.get("/products")
def get_all_products():
    session = SessionLocal()
    products = session.query(ProductMaster).all()
    session.close()
    return [
        {"code": product.code, "name": product.name, "price": product.price}
        for product in products
    ]
