from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from app.database import supabase
from app.services.notifications import send_web_push

router = APIRouter(tags=["Notifications"])

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")

class SubscriptionKeys(BaseModel):
    p256dh: str
    auth: str

class PushSubscription(BaseModel):
    endpoint: str
    keys: SubscriptionKeys
    user_id: str

@router.get("/public-key")
async def get_public_key():
    """ 取得 VAPID 公鑰供前端 Service Worker 訂閱使用 """
    if not VAPID_PUBLIC_KEY:
        raise HTTPException(status_code=500, detail="VAPID_PUBLIC_KEY not configured on server")
    return {"public_key": VAPID_PUBLIC_KEY}

@router.post("/subscribe")
async def subscribe(sub: PushSubscription):
    """ 儲存前端發送過來的瀏覽器推播金鑰 """
    # 確保該 User ID 是有效的
    user_res = supabase.table("profiles").select("id").eq("id", sub.user_id).execute()
    if not user_res.data:
        raise HTTPException(status_code=404, detail="User not found")
        
    data = {
        "user_id": sub.user_id,
        "endpoint": sub.endpoint,
        "keys_p256dh": sub.keys.p256dh,
        "keys_auth": sub.keys.auth
    }
    
    try:
        # 使用 upsert 避免重複寫入相同裝置的 key (基於 UNIQUE 限制)
        supabase.table("push_subscriptions").upsert(data, on_conflict="user_id, endpoint").execute()
        
        # 立即發送一則測試通知，讓爸爸知道設定成功
        test_payload = {
            "title": "✅ 推播設定成功",
            "body": "您已成功啟用血壓提醒！未來我會準時督促您測量血壓喔。",
            "url": "/"
        }
        sub_info = {
            "endpoint": sub.endpoint, 
            "keys": {"p256dh": sub.keys.p256dh, "auth": sub.keys.auth}
        }
        send_web_push(sub_info, test_payload)
        
        return {"success": True, "message": "訂閱已儲存並發送測試通知"}
    except Exception as e:
        print(f"🚨 Subscribe Error: {e}")
        raise HTTPException(status_code=500, detail="無法儲存訂閱資料")
