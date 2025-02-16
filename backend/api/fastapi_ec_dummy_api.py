from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from azure.cosmos import CosmosClient
import uuid
import random

app = FastAPI()

# Cosmos DB 接続情報
COSMOS_DB_URL = "https://chatbotdb274.documents.azure.com:443/"
COSMOS_DB_KEY = "xo18BnffDOis94SwdI0RvjxiPEUKnXVrtKa7APVSGTjjAgtevdkceLrX2RSPM9vtkyQkw9hOJX0zACDbehce5w=="
DATABASE_NAME = "chatbotdb"
PRODUCTS_CONTAINER = "products"
ORDERS_CONTAINER = "orders"
FAQS_CONTAINER = "faqs"

client = CosmosClient(COSMOS_DB_URL, COSMOS_DB_KEY)
database = client.get_database_client(DATABASE_NAME)
products_container = database.get_container_client(PRODUCTS_CONTAINER)
orders_container = database.create_container_if_not_exists(id=ORDERS_CONTAINER, partition_key={"paths": ["/user_id"], "kind": "Hash"})
faqs_container = database.create_container_if_not_exists(id=FAQS_CONTAINER, partition_key={"paths": ["/question_id"], "kind": "Hash"})

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/products")
def get_products(
    category: str = Query(None, description="カテゴリでフィルター"),
    brand: str = Query(None, description="ブランドでフィルター"),
    min_price: int = Query(None, description="最低価格でフィルター"),
    max_price: int = Query(None, description="最高価格でフィルター"),
    search: str = Query(None, description="商品名の部分検索"),
    sort_by: str = Query(None, description="並び替え基準 (price/stock)"),
    order: str = Query("asc", description="昇順 (asc) または 降順 (desc)"),
    page: int = Query(1, description="ページ番号"),
    page_size: int = Query(10, description="1ページのアイテム数")
):
    """化粧品を取得（フィルター、検索、並び替え、ページネーション付き）"""
    query = "SELECT * FROM c"
    filters = []

    if category:
        filters.append(f"c.category = '{category}'")
    if brand:
        filters.append(f"c.brand = '{brand}'")
    if min_price:
        filters.append(f"c.price >= {min_price}")
    if max_price:
        filters.append(f"c.price <= {max_price}")

    if filters:
        query += " WHERE " + " AND ".join(filters)
    
    items = list(products_container.query_items(query=query, enable_cross_partition_query=True))
    
    # 商品名の部分検索
    if search:
        items = [item for item in items if search in item["name"]]
    
    # 並び替え
    if sort_by in ["price", "stock"]:
        reverse = order == "desc"
        items.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
    
    # ページネーション
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_items = items[start_idx:end_idx]
    
    return {"products": paginated_items, "total": len(items)}

@app.get("/orders/{user_id}")
def get_orders_by_user(user_id: str):
    """ユーザーごとの注文を取得"""
    query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
    items = list(orders_container.query_items(query=query, enable_cross_partition_query=True))
    return {"orders": items}

@app.get("/faq")
def get_faq():
    """FAQ を取得"""
    query = "SELECT * FROM c"
    items = list(faqs_container.query_items(query=query, enable_cross_partition_query=True))
    return {"faq": items}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)