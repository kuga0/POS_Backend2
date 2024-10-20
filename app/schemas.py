from pydantic import BaseModel
from typing import List, Optional

# 商品検索用のリクエストとレスポンスのスキーマ
class ProductRequest(BaseModel):
    code: str

class ProductResponse(BaseModel):
    code: str
    name: str
    price: int

# 購入リクエスト/レスポンス用のスキーマ
class PurchaseItem(BaseModel):
    code: str
    name: str
    price: int

class PurchaseRequest(BaseModel):
    emp_code: Optional[str] = "9999999999"  # デフォルト値
    store_code: str
    pos_id: str
    items: List[PurchaseItem]

class PurchaseResponse(BaseModel):
    success: bool
    total_amount: int
    total_amount_ex_tax: int

# 商品リストの取得用スキーマ
class ProductListResponse(BaseModel):
    products: List[ProductResponse]
