from azure.cosmos import CosmosClient

# 连接到 Cosmos DB
COSMOS_DB_URL = "https://chatbotdb274.documents.azure.com:443/"

client = CosmosClient(COSMOS_DB_URL, COSMOS_DB_KEY)

# 创建数据库
DATABASE_NAME = "chatbotdb"
database = client.create_database_if_not_exists(id=DATABASE_NAME)

# 创建 Container（商品数据）
CONTAINER_NAME = "products"
container = database.create_container_if_not_exists(
    id=CONTAINER_NAME,
    partition_key={"paths": ["/category"], "kind": "Hash"},
    offer_throughput=400  # 设置吞吐量
)

# 插入 Dummy 商品数据
products = [
    {"id": "1", "name": "欧莱雅保湿霜", "category": "skincare", "brand": "欧莱雅", "price": 199.99, "stock": 50},
    {"id": "2", "name": "资生堂眼霜", "category": "skincare", "brand": "资生堂", "price": 299.99, "stock": 30},
    {"id": "3", "name": "Dior 口红", "category": "makeup", "brand": "Dior", "price": 399.99, "stock": 20},
]

for product in products:
    container.upsert_item(product)

print("Dummy 商品数据已存入 Cosmos DB")

query = "SELECT * FROM c WHERE c.category='skincare'"
items = list(container.query_items(query=query, enable_cross_partition_query=True))

for item in items:
    print(item)