from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount, ActivityTypes
import httpx
import logging

FASTAPI_URL = "https://bytex-appservice-hphddwgad7edfda4.japaneast-01.azurewebsites.net/"  # FastAPI の URL
logging.basicConfig(level=logging.INFO)

class MyBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        user_message = turn_context.activity.text or ""
        logging.info(f"受信メッセージ: {user_message}")
        
        if "商品" in user_message:
            response_text = await self.fetch_products()
        elif "注文" in user_message:
            response_text = await self.fetch_orders("user_1")  # 変更済みのユーザーID
        elif "おすすめ" in user_message:
            response_text = await self.recommend_products()
        elif "寒い" in user_message:
            response_text = "寒い時期には、保湿クリームやリップバームがおすすめです！"
        elif "暑い" in user_message:
            response_text = "暑い季節には、日焼け止めや冷却ミストを使うと快適です！"
        else:
            response_text = f"あなたのメッセージ: {user_message}"
        
        await turn_context.send_activity(response_text)
    
    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("こんにちは！スキンケア・化粧品のチャットボットです。お探しの商品やおすすめがあれば教えてください！")

    async def on_turn(self, turn_context: TurnContext):
        if not hasattr(turn_context.activity, "text") or turn_context.activity.text is None:
            logging.warning(f"受信したアクティビティに 'text' がありません: {turn_context.activity}")
            await turn_context.send_activity("メッセージがありません。")
            return
        
        if turn_context.activity.type == ActivityTypes.message:
            await self.on_message_activity(turn_context)
        elif turn_context.activity.type == ActivityTypes.conversation_update:
            await self.on_members_added_activity(turn_context.activity.members_added, turn_context)
        else:
            await turn_context.send_activity("メッセージのみ対応しています。")

    async def fetch_products(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FASTAPI_URL}/products?category=スキンケア")
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", [])
                return "\n".join([f"{p['name']} ({p['price']}円)" for p in products][:5])
            return "商品が見つかりませんでした。"

    async def fetch_orders(self, user_id):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FASTAPI_URL}/orders/{user_id}")
            logging.info(f"注文 API 応答: {response.status_code}, 内容: {response.text}")
            if response.status_code == 200:
                data = response.json()
                orders = data.get("orders", [])
                if not orders:
                    return "注文が見つかりませんでした。"
                return "\n".join([f"注文: {o['id']} - 状態: {o['order_status']}" for o in orders])
            return "注文 API の取得に失敗しました。"

    async def recommend_products(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FASTAPI_URL}/products?sort_by=price&order=desc")
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", [])
                return "\n".join([f"おすすめ: {p['name']} ({p['price']}円)" for p in products][:3])
            return "おすすめ商品が見つかりませんでした。"
